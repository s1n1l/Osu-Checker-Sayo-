"""Analogue key travel from a SayoDevice O3C over HID.

The protocol is request/response, not a stream: the device stays silent
until asked. The web configurator polls it about 20 times a second, which
makes it look like a stream from the outside.

The real ceiling depends on the USB polling rate set on the device. At
8000 Hz one round trip takes about 0.37 ms, roughly three USB frames, so
all three keys can be sampled around 2600 times a second.

Request, usage page 0xFF12, 1024 byte packet:

    0x00 report_id 0x22
    0x01 echo 0x03
    0x02 checksum u16 LE, the packet summed as u16 with the slot zeroed
    0x04 len u16 LE = 0x0004
    0x06 id 0x15
    0x07 index 0x01

Reply: len 0x000a, then three u16 values, key travel in micrometres,
0 at rest and 4000 at the full 4 mm. Index 0 returns the raw ADC of one
key and index 2 the raw ADC of all three.

Only read requests are sent; device configuration is never touched.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable

import hid

VID, PID = 0x8089, 0x0009
UP_STATUS = 0xFF12
UP_SCOPE = 0xFF11
SUBCMD_KEY_STATUS = 0x15
INDEX_TRAVEL_UM = 0x01
REPORT_ID_HS = 0x22
ECHO = 0x03
PACKET_SIZE = 1024
DEFAULT_HZ = 1500.0
UNLIMITED_HZ = 1500.0
FULL_TRAVEL_UM = 4000
NUM_KEYS = 3


@dataclass
class TravelSample:
    t: float
    um: tuple[int, ...]


def find_interface(usage_page: int) -> bytes | None:
    for d in hid.enumerate(VID, PID):
        if d["usage_page"] == usage_page:
            return d["path"]
    return None


def device_present() -> bool:
    return find_interface(UP_STATUS) is not None


def checksum(pkt: bytearray) -> int:
    pkt[2] = 0
    pkt[3] = 0
    total = 0
    for i in range(0, len(pkt), 2):
        total = (total + (pkt[i] | (pkt[i + 1] << 8))) & 0xFFFF
    return total


def build_request(cmd_id: int, index: int, size: int = PACKET_SIZE,
                  report_id: int = REPORT_ID_HS) -> bytes:
    pkt = bytearray(size)
    pkt[0] = report_id
    pkt[1] = ECHO
    pkt[4] = 0x04
    pkt[5] = 0x00
    pkt[6] = cmd_id
    pkt[7] = index
    ck = checksum(pkt)
    pkt[2] = ck & 0xFF
    pkt[3] = (ck >> 8) & 0xFF
    return bytes(pkt)


TRAVEL_REQUEST = build_request(SUBCMD_KEY_STATUS, INDEX_TRAVEL_UM)


def decode_status(pkt: bytes) -> tuple[int, ...] | None:
    """Key travel from a reply to request 0x15 with index 1."""
    if len(pkt) < 8 + NUM_KEYS * 2:
        return None
    if pkt[6] != SUBCMD_KEY_STATUS or pkt[7] != INDEX_TRAVEL_UM:
        return None
    vals = []
    for k in range(NUM_KEYS):
        v = pkt[8 + k * 2] | (pkt[9 + k * 2] << 8)
        if v > 60000:
            v = 0
        vals.append(v)
    return tuple(vals)


class SayoTravelReader:
    """Background poller for analogue key travel."""

    def __init__(self, on_sample: Callable[[TravelSample], None] | None = None,
                 keep: int = 4_000_000, hz: float = DEFAULT_HZ):
        self.on_sample = on_sample
        self.hz = hz
        self.misses = 0
        self.samples: list[TravelSample] = []
        self.keep = keep
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self.error: str | None = None
        self.packets = 0

    def start(self) -> bool:
        path = find_interface(UP_STATUS)
        if not path:
            self.error = "SayoDevice O3C not found (interface 0xFF12)"
            return False
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, args=(path,),
                                        daemon=True, name="sayo-travel")
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def snapshot(self) -> list[TravelSample]:
        with self._lock:
            return list(self.samples)

    def clear(self) -> None:
        with self._lock:
            self.samples.clear()
        self.packets = 0

    def _run(self, path: bytes) -> None:
        try:
            dev = hid.device()
            dev.open_path(path)
            dev.set_nonblocking(0)
        except Exception as exc:
            self.error = f"cannot open HID: {exc}"
            return
        throttled = 0 < self.hz < UNLIMITED_HZ
        interval = 1.0 / self.hz if throttled else 0.0
        next_at = time.perf_counter()
        try:
            while not self._stop.is_set():
                cycle_start = time.perf_counter()
                try:
                    dev.write(TRAVEL_REQUEST)
                except Exception:
                    break
                deadline = cycle_start + 0.005
                um = None
                while time.perf_counter() < deadline:
                    r = dev.read(PACKET_SIZE, 3)
                    if not r:
                        continue
                    um = decode_status(bytes(r))
                    if um is not None:
                        break
                if um is None:
                    self.misses += 1
                    continue
                t = time.perf_counter()
                self.packets += 1
                sample = TravelSample(t, um)
                with self._lock:
                    self.samples.append(sample)
                    if len(self.samples) > self.keep:
                        del self.samples[: self.keep // 4]
                if self.on_sample:
                    self.on_sample(sample)
                if not throttled:
                    continue
                next_at += interval
                rest = next_at - time.perf_counter()
                if rest > 0:
                    time.sleep(rest)
                elif rest < -interval * 4:
                    next_at = time.perf_counter()
        finally:
            try:
                dev.close()
            except Exception:
                pass


def travel_events(samples: list[TravelSample], key: int,
                  trigger_um: int, release_um: int) -> list[dict]:
    """Rebuilds presses from the analogue signal at the given thresholds.

    Comparing these against the HID events shows whether Rapid Trigger is
    responsible for a press the game did or did not see.
    """
    events: list[dict] = []
    down = False
    cur: dict | None = None
    for s in samples:
        if key >= len(s.um):
            continue
        v = s.um[key]
        if not down and v >= trigger_um:
            down = True
            cur = {"press": s.t, "peak": v}
        elif down:
            cur["peak"] = max(cur["peak"], v)
            if v <= release_um:
                down = False
                cur["release"] = s.t
                cur["min_after"] = v
                events.append(cur)
                cur = None
    if cur is not None:
        cur["release"] = samples[-1].t if samples else cur["press"]
        cur["min_after"] = 0
        events.append(cur)
    return events

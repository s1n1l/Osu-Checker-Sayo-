"""Records a play session: key presses, analogue travel and cursor.

Three things matter here. Windows auto-repeat sends a key down every ~30 ms
while a key is held, so repeats are filtered by key state. Only keys from
the O3C are recorded, by default only while osu! has focus. And which keys
those are comes from the settings: the device reports travel for its three
slots in a fixed order, so a press is stored with the slot it came from
and the label is only for display.
"""
from __future__ import annotations

import bisect
import ctypes
import json
import time
from ctypes import wintypes
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .device.cursor import (CursorRecorder, PlayfieldRect, client_rect_on_screen,
                            playfield_from_client)
from .device.keys import DEFAULT_CODES, NUM_KEYS, key_name, normalise
from .device.rawinput import RawKeyboardListener
from .device.sayo import SayoTravelReader, TravelSample

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

LEGACY_SLOTS = {"P": 0, "V": 1, "B": 2}


def foreground_process() -> str:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ""
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return ""
    try:
        size = wintypes.DWORD(1024)
        buf = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return Path(buf.value).name.lower()
    finally:
        kernel32.CloseHandle(h)
    return ""


def is_osu_focused() -> bool:
    return foreground_process() in ("osu!.exe", "osu!.exe".lower(), "osu.exe")


@dataclass
class Press:
    key: str
    press: float
    release: float | None = None
    slot: int = -1

    @property
    def hold(self) -> float | None:
        return None if self.release is None else (self.release - self.press) * 1000.0


@dataclass
class Session:
    started_at: float = 0.0
    presses: list[Press] = field(default_factory=list)
    travel: list[tuple[float, tuple[int, ...]]] = field(default_factory=list)
    cursor: list[tuple[float, int, int]] = field(default_factory=list)
    playfield: tuple[float, float, float, float] | None = None
    repeats_filtered: int = 0
    only_when_focused: bool = True
    key_codes: list[int] = field(default_factory=lambda: list(DEFAULT_CODES))

    @property
    def key_labels(self) -> list[str]:
        return [key_name(c) for c in normalise(self.key_codes)]

    def slot_of(self, press: "Press") -> int:
        """Device slot of a press, including recordings from older builds."""
        if press.slot >= 0:
            return press.slot
        return LEGACY_SLOTS.get(press.key, -1)

    def to_json(self) -> dict:
        return {
            "started_at": self.started_at,
            "only_when_focused": self.only_when_focused,
            "repeats_filtered": self.repeats_filtered,
            "key_codes": list(normalise(self.key_codes)),
            "presses": [asdict(p) for p in self.presses],
            "travel": [[round(t, 5), list(v)] for t, v in self.travel],
            "cursor": [[round(t, 5), x, y] for t, x, y in self.cursor],
            "playfield": list(self.playfield) if self.playfield else None,
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_json()), encoding="utf-8")

    @staticmethod
    def load(path: str | Path) -> "Session":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        s = Session(started_at=d.get("started_at", 0.0),
                    repeats_filtered=d.get("repeats_filtered", 0),
                    only_when_focused=d.get("only_when_focused", True),
                    key_codes=normalise(d.get("key_codes")))
        s.presses = [Press(**p) for p in d.get("presses", [])]
        s.travel = [(t, tuple(v)) for t, v in d.get("travel", [])]
        s.cursor = [(t, x, y) for t, x, y in d.get("cursor", [])]
        pf = d.get("playfield")
        s.playfield = tuple(pf) if pf else None
        return s

    def playfield_rect(self) -> PlayfieldRect | None:
        return PlayfieldRect(*self.playfield) if self.playfield else None

    def cursor_in_playfield(self) -> list[tuple[float, float, float]]:
        """Cursor in playfield coordinates, 512x384."""
        pf = self.playfield_rect()
        if pf is None:
            return []
        return [(t, *pf.to_playfield(x, y)) for t, x, y in self.cursor]

    def depth_report(self, trigger_um: int = 500,
                     release_um: int = 400) -> dict:
        """How deep the keys are actually pressed.

        Travel is polled independently of the presses, so every press is covered
        by several samples and the maximum inside a press is taken as its depth.
        """
        out: dict = {"trigger_um": trigger_um, "release_um": release_um,
                     "keys": {}}
        if not self.travel:
            return out
        times = [t for t, _ in self.travel]
        for idx, key in enumerate(self.key_labels):
            peaks: list[int] = []
            for p in self.presses:
                if self.slot_of(p) != idx or p.release is None:
                    continue
                lo = bisect.bisect_left(times, p.press)
                hi = bisect.bisect_right(times, p.release)
                best = -1
                for i in range(lo, hi):
                    v = self.travel[i][1]
                    if idx < len(v) and v[idx] > best:
                        best = v[idx]
                if best >= 0:
                    peaks.append(best)
            if len(peaks) < 5:
                continue
            peaks.sort()
            out["keys"][key] = {
                "n": len(peaks),
                "median": peaks[len(peaks) // 2],
                "p10": peaks[int(len(peaks) * 0.10)],
                "min": peaks[0],
                "bottomed": sum(1 for v in peaks if v >= 3900) / len(peaks),
                "margin_p10": peaks[int(len(peaks) * 0.10)] - trigger_um,
            }
        if out["keys"]:
            worst = min(out["keys"].values(), key=lambda d: d["margin_p10"])
            out["peak_depth_um"] = worst["p10"]
        return out

    def peak_depth(self, slot: int) -> list[int]:
        """Maximum depth within each press of one device slot, in µm."""
        if not 0 <= slot < NUM_KEYS or not self.travel:
            return []
        idx = slot
        times = [t for t, _ in self.travel]
        out = []
        for p in self.presses:
            if self.slot_of(p) != slot or p.release is None:
                continue
            lo = bisect.bisect_left(times, p.press)
            hi = bisect.bisect_right(times, p.release)
            best = -1
            for i in range(lo, hi):
                v = self.travel[i][1]
                if idx < len(v) and v[idx] > best:
                    best = v[idx]
            if best >= 0:
                out.append(best)
        return out


class SessionRecorder:
    def __init__(self, only_when_focused: bool = True,
                 analog_hz: float = 500.0, key_codes=None):
        self.key_codes = normalise(key_codes)
        self.session = Session(only_when_focused=only_when_focused,
                               key_codes=list(self.key_codes))
        self.analog_hz = analog_hz
        self._down: dict[str, Press] = {}
        self._t0 = 0.0
        self._kb: RawKeyboardListener | None = None
        self._sayo: SayoTravelReader | None = None
        self._cursor: CursorRecorder | None = None
        self.running = False
        self.error: str | None = None
        self.warning: str | None = None
        self.analog_available = False

    def start(self) -> bool:
        self._t0 = time.perf_counter()
        self.session = Session(started_at=time.time(),
                               only_when_focused=self.session.only_when_focused,
                               key_codes=list(self.key_codes))
        self._down.clear()
        self._sayo = SayoTravelReader(on_sample=self._on_travel,
                                      hz=self.analog_hz)
        self.analog_available = self._sayo.start()
        if not self.analog_available:
            self.warning = self._sayo.error

        self._cursor = CursorRecorder()
        self._cursor.start(self._t0)
        self._capture_playfield()

        self._kb = RawKeyboardListener(on_key=self._on_key)
        if not self._kb.start():
            self.error = self._kb.error or "Raw Input listener did not start"
            if self.analog_available:
                self._sayo.stop()
            self._cursor.stop()
            return False
        self.running = True
        return True

    def stop(self) -> Session:
        if self._kb:
            self._kb.stop()
        if self._sayo and self.analog_available:
            self._sayo.stop()
        if self._cursor:
            self._cursor.stop()
            self.session.cursor = self._cursor.snapshot()
        self.running = False
        for p in self._down.values():
            if p.release is None:
                p.release = time.perf_counter() - self._t0
        self._down.clear()
        return self.session

    def _capture_playfield(self) -> None:
        """Reads playfield geometry from the osu! window while it is focused."""
        if not is_osu_focused():
            return
        hwnd = user32.GetForegroundWindow()
        rect = client_rect_on_screen(hwnd)
        if rect:
            pf = playfield_from_client(*rect)
            self.session.playfield = (pf.x, pf.y, pf.w, pf.h)

    def _on_travel(self, s: TravelSample) -> None:
        self.session.travel.append((s.t - self._t0, s.um))

    def _on_key(self, k) -> None:
        if k.vkey not in self.key_codes:
            return
        slot = self.key_codes.index(k.vkey)
        name = key_name(k.vkey)
        if self.session.only_when_focused and not is_osu_focused():
            return
        if self.session.playfield is None:
            self._capture_playfield()
        t = k.t - self._t0
        if k.down:
            if name in self._down:
                self.session.repeats_filtered += 1
                return
            p = Press(key=name, press=t, slot=slot)
            self._down[name] = p
            self.session.presses.append(p)
        else:
            p = self._down.pop(name, None)
            if p is not None:
                p.release = t

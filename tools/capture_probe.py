"""Calibration capture for the O3C.

Records all-key travel, the 16 sample scope and real key presses at the
same time. Nothing is written to the device.
"""
import json, sys, threading, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hid
from osuchecker.device.rawinput import RawKeyboardListener

VID, PID = 0x8089, 0x0009
VK = {0x50: "P", 0x56: "V", 0x42: "B"}
STOP = threading.Event()
LOG, LOCK = [], threading.Lock()
T0 = time.perf_counter()


def find(up):
    for d in hid.enumerate(VID, PID):
        if d["usage_page"] == up:
            return d["path"]


def reader(up, name):
    path = find(up)
    if not path:
        print(f"[{name}] not found")
        return
    dev = hid.device(); dev.open_path(path); dev.set_nonblocking(1)
    try:
        while not STOP.is_set():
            r = dev.read(1024)
            if not r:
                time.sleep(0.0002); continue
            t = time.perf_counter() - T0
            with LOCK:
                LOG.append({"t": round(t, 6), "src": name, "d": bytes(r).hex()})
    finally:
        dev.close()


def on_key(k):
    with LOCK:
        LOG.append({"t": round(k.t - T0, 6), "src": "key",
                    "k": VK.get(k.vkey, hex(k.vkey)), "down": k.down})


STEPS = [
    ("Touch nothing, measuring the rest level", 3),
    ("Press ONLY V, five times, with pauses", 7),
    ("Press ONLY B, five times, with pauses", 7),
    ("Hold ONLY V for about 2 s, then release", 5),
    ("Hold ONLY B for about 2 s, then release", 5),
    ("Alternate V and B as fast as you can", 6),
]


def main():
    threads = [threading.Thread(target=reader, args=(0xFF11, "ff11"), daemon=True),
               threading.Thread(target=reader, args=(0xFF12, "ff12"), daemon=True)]
    for t in threads:
        t.start()
    kb = RawKeyboardListener(on_key=on_key)
    if not kb.start():
        print("Raw Input listener did not start:", kb.error)
    time.sleep(0.3)

    marks = []
    print("\n" + "=" * 60)
    for text, secs in STEPS:
        marks.append({"label": text, "start": round(time.perf_counter() - T0, 3),
                      "dur": secs})
        for left in range(secs, 0, -1):
            print(f"\r  >> {text:<44s} {left:2d}s ", end="", flush=True)
            time.sleep(1)
        print(f"\r  ok {text:<44s}     ")
    print("=" * 60)

    STOP.set()
    kb.stop()
    for t in threads:
        t.join(timeout=1.5)

    with LOCK:
        rows = sorted(LOG, key=lambda r: r["t"])
    with open("capture_raw.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps({"src": "meta", "marks": marks}, ensure_ascii=False) + "\n")
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    c = {}
    for r in rows:
        c[r["src"]] = c.get(r["src"], 0) + 1
    print(f"\nrecorded {len(rows)} events: {c}")
    keys = [r for r in rows if r["src"] == "key"]
    print(f"presses from the O3C: {sum(1 for k in keys if k['down'])} "
          f"({sorted({k['k'] for k in keys})})")
    print("file: capture_raw.jsonl")


main()

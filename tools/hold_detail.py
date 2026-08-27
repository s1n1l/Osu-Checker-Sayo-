"""Timeline of the hold phases of a capture.

Shows HID key events next to the analogue travel, which is what separates
a real double actuation from Windows key auto-repeat.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CAPTURE = Path("capture_raw.jsonl")
PHASES = (("HOLD V", 17.31, 22.31, "V", 1), ("HOLD B", 22.31, 27.31, "B", 2))


def decode_status(hex_data):
    b = bytes.fromhex(hex_data)
    if len(b) < 14 or b[6] != 0x15:
        return None
    return [(0 if (b[8 + k * 2] | (b[9 + k * 2] << 8)) > 60000
             else (b[8 + k * 2] | (b[9 + k * 2] << 8))) for k in range(3)]


def main():
    if not CAPTURE.exists():
        print(f"{CAPTURE} not found, run tools/capture_probe.py first")
        return 1
    rows = [json.loads(line) for line in CAPTURE.open(encoding="utf-8")][1:]

    for label, t0, t1, key, index in PHASES:
        print(f"\n{'=' * 72}\n{label}  (phase {t0:.1f}-{t1:.1f} s)\n{'=' * 72}")
        events = [r for r in rows
                  if r["src"] == "key" and t0 <= r["t"] < t1 and r["k"] == key]
        downs = [e["t"] for e in events if e["down"]]
        ups = [e for e in events if not e["down"]]
        print(f"HID events from the device: {len(downs)} down / {len(ups)} up")
        if len(downs) > 1:
            gaps = sorted((downs[i] - downs[i - 1]) * 1000
                          for i in range(1, len(downs)))
            print(f"gaps between downs, ms: min={gaps[0]:.1f} "
                  f"median={gaps[len(gaps) // 2]:.1f} max={gaps[-1]:.1f}")

        travel = []
        for r in rows:
            if r["src"] != "ff12" or not t0 <= r["t"] < t1:
                continue
            values = decode_status(r["d"])
            if values:
                travel.append((r["t"], values[index]))
        if travel:
            only = [v for _, v in travel]
            print(f"key travel ff12, um: min={min(only)} max={max(only)} "
                  f"samples={len(only)}")

        merged = [(e["t"], "HID " + ("DOWN" if e["down"] else "UP  "), None)
                  for e in events]
        merged += [(t, "analogue    ", v) for t, v in travel]
        merged.sort()
        print("\n  time(s)  event         travel um")
        for t, what, value in merged[:34]:
            print(f"  {t:7.4f}  {what}   {'' if value is None else value}")
    return 0


sys.exit(main())

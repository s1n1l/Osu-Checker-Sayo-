"""Summarises a capture produced by tools/capture_probe.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CAPTURE = Path("capture_raw.jsonl")


def decode_status(hex_data):
    b = bytes.fromhex(hex_data)
    if len(b) < 14 or b[6] != 0x15:
        return None
    out = []
    for k in range(3):
        v = b[8 + k * 2] | (b[9 + k * 2] << 8)
        out.append(0 if v > 60000 else v)
    return out


def decode_scope(hex_data):
    b = bytes.fromhex(hex_data)
    if (b[4] | (b[5] << 8)) != 0x27:
        return None
    return [b[o] | (b[o + 1] << 8) for o in range(0x0A, 0x2A, 2)], b[0x2A]


def main():
    if not CAPTURE.exists():
        print(f"{CAPTURE} not found, run tools/capture_probe.py first")
        return 1
    rows = [json.loads(line) for line in CAPTURE.open(encoding="utf-8")]
    meta, rows = rows[0], rows[1:]
    keys = [r for r in rows if r["src"] == "key"]
    status = [r for r in rows if r["src"] == "ff12"]
    scope = [r for r in rows if r["src"] == "ff11"]
    print(f"events: key={len(keys)} ff12={len(status)} ff11={len(scope)}\n")

    header = f"{'phase':42} | {'presses':16} | {'peak travel um':22} | ff11"
    print(header)
    print("-" * len(header))
    for mark in meta["marks"]:
        t0, t1 = mark["start"], mark["start"] + mark["dur"]
        pressed = {}
        for r in keys:
            if t0 <= r["t"] < t1 and r["down"]:
                pressed[r["k"]] = pressed.get(r["k"], 0) + 1
        peak = [0, 0, 0]
        for r in status:
            if not t0 <= r["t"] < t1:
                continue
            values = decode_status(r["d"])
            if values:
                peak = [max(a, b) for a, b in zip(peak, values)]
        low, high, moves = 1 << 30, 0, 0
        for r in scope:
            if not t0 <= r["t"] < t1:
                continue
            decoded = decode_scope(r["d"])
            if not decoded:
                continue
            samples = decoded[0]
            low = min(low, min(samples))
            high = max(high, max(samples))
            if max(samples) - min(samples) > 200:
                moves += 1
        low = 0 if low > (1 << 29) else low
        print(f"{mark['label'][:42]:42} | {str(pressed or '-'):16} | "
              f"{str(peak):22} | range {low:5}..{high:<6} moves={moves}")
    return 0


sys.exit(main())

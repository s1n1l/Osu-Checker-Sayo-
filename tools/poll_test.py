"""Confirms that the O3C speaks request/response rather than streaming.

With nothing sent the device is silent; every read request gets exactly one
reply back.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hid

from osuchecker.device.sayo import build_request, find_interface

INTERFACES = ((0xFF12, 0x22, 1024, "ff12 (all-key status)"),
              (0xFF11, 0x21, 64, "ff11 (scope)"))
COMMANDS = (0x15, 0x1F, 0x1E, 0x02)


def main():
    for usage_page, report_id, size, label in INTERFACES:
        path = find_interface(usage_page)
        if not path:
            print(f"{label}: interface not found")
            continue
        dev = hid.device()
        dev.open_path(path)
        dev.set_nonblocking(1)
        print(f"\n=== {label}")

        idle = 0
        deadline = time.perf_counter() + 0.7
        while time.perf_counter() < deadline:
            if dev.read(1024):
                idle += 1
            else:
                time.sleep(0.0005)
        print(f"  with no requests sent: {idle} packets")

        for command in COMMANDS:
            replies = []
            for _ in range(10):
                dev.write(build_request(command, 0, size, report_id))
                until = time.perf_counter() + 0.05
                while time.perf_counter() < until:
                    data = dev.read(1024)
                    if data:
                        replies.append(bytes(data))
                        break
                    time.sleep(0.0003)
            sample = f"  sample: {replies[0][:16].hex(' ')}" if replies else ""
            print(f"  request {command:#04x} x10 -> {len(replies)} replies{sample}")
        dev.close()
    return 0


sys.exit(main())

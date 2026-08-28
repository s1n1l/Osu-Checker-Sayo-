"""Virtual key codes and the names shown for them.

The device reports analogue travel for its three keys in a fixed order, so
a bound key is stored as the virtual key code sitting in that slot: slot 0
is the first key on the device, slot 1 the second, slot 2 the third.
What the key is bound to in the device configurator is up to the user, so
nothing here is hard coded to one layout.
"""
from __future__ import annotations

NUM_KEYS = 3
DEFAULT_CODES = (0x50, 0x56, 0x42)  # P, V, B

_NAMED = {
    0x08: "Backspace", 0x09: "Tab", 0x0D: "Enter", 0x13: "Pause",
    0x14: "Caps Lock", 0x1B: "Esc", 0x20: "Space", 0x21: "Page Up",
    0x22: "Page Down", 0x23: "End", 0x24: "Home", 0x25: "Left",
    0x26: "Up", 0x27: "Right", 0x28: "Down", 0x2C: "Print Screen",
    0x2D: "Insert", 0x2E: "Delete",
    0x5B: "Left Win", 0x5C: "Right Win", 0x5D: "Menu",
    0x6A: "Num *", 0x6B: "Num +", 0x6D: "Num −", 0x6E: "Num .",
    0x6F: "Num /", 0x90: "Num Lock", 0x91: "Scroll Lock",
    0xA0: "Left Shift", 0xA1: "Right Shift", 0xA2: "Left Ctrl",
    0xA3: "Right Ctrl", 0xA4: "Left Alt", 0xA5: "Right Alt",
    0xBA: ";", 0xBB: "=", 0xBC: ",", 0xBD: "-", 0xBE: ".", 0xBF: "/",
    0xC0: "`", 0xDB: "[", 0xDC: "\\", 0xDD: "]", 0xDE: "'",
}
for _c in range(0x30, 0x3A):
    _NAMED[_c] = chr(_c)
for _c in range(0x41, 0x5B):
    _NAMED[_c] = chr(_c)
for _n in range(10):
    _NAMED[0x60 + _n] = f"Num {_n}"
for _n in range(1, 25):
    _NAMED[0x6F + _n] = f"F{_n}"

IGNORED = {0x00, 0xFF, 0x10, 0x11, 0x12}  # unset and the generic modifiers


def key_name(code: int) -> str:
    """Label for a virtual key code."""
    return _NAMED.get(code, f"VK {code:02X}")


def normalise(codes) -> list[int]:
    """Three usable key codes, padded from the defaults."""
    out: list[int] = []
    for value in list(codes or [])[:NUM_KEYS]:
        try:
            code = int(value)
        except (TypeError, ValueError):
            continue
        if 0 < code < 0x100:
            out.append(code)
    while len(out) < NUM_KEYS:
        out.append(DEFAULT_CODES[len(out)])
    return out


def labels(codes) -> list[str]:
    return [key_name(c) for c in normalise(codes)]


def slot_of(codes, code: int) -> int | None:
    """Which device slot a virtual key code is bound to."""
    for i, bound in enumerate(normalise(codes)):
        if bound == code:
            return i
    return None

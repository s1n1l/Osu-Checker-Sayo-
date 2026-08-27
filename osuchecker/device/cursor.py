"""Records cursor position during play.

Polling rather than Raw Input: a tablet under OpenTabletDriver in absolute
mode delivers its position through synthesised input, which Raw Input
reports either without a device handle or without absolute coordinates.
GetCursorPos returns the resulting position whatever driver produced it.
"""
from __future__ import annotations

import ctypes
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetCursorPos.argtypes = [ctypes.c_void_p]
user32.GetCursorPos.restype = wintypes.BOOL
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.c_void_p]
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.c_void_p]

PLAYFIELD_W, PLAYFIELD_H = 512.0, 384.0


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


@dataclass
class PlayfieldRect:
    """Where the osu! playfield sits on screen."""
    x: float
    y: float
    w: float
    h: float

    def to_playfield(self, sx: float, sy: float) -> tuple[float, float]:
        if self.w <= 0 or self.h <= 0:
            return 0.0, 0.0
        return ((sx - self.x) / self.w * PLAYFIELD_W,
                (sy - self.y) / self.h * PLAYFIELD_H)


def client_rect_on_screen(hwnd) -> tuple[int, int, int, int] | None:
    r = RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(r)):
        return None
    p = POINT(r.left, r.top)
    if not user32.ClientToScreen(hwnd, ctypes.byref(p)):
        return None
    return p.x, p.y, r.right - r.left, r.bottom - r.top


def playfield_from_client(cx: int, cy: int, cw: int, ch: int) -> PlayfieldRect:
    """osu!stable playfield: 512x384 centred in a 640x480 virtual screen.

    The field sits about 8 virtual pixels below the centre.
    """
    ratio = ch / 480.0
    pw, ph = PLAYFIELD_W * ratio, PLAYFIELD_H * ratio
    return PlayfieldRect(x=cx + (cw - pw) / 2.0,
                         y=cy + (ch - ph) / 2.0 + 8.0 * ratio,
                         w=pw, h=ph)


class CursorRecorder:
    """Polls the cursor position on its own thread."""

    def __init__(self, hz: float = 500.0):
        self.interval = 1.0 / hz
        self.samples: list[tuple[float, int, int]] = []
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._t0 = 0.0

    def start(self, t0: float | None = None) -> bool:
        self._t0 = t0 if t0 is not None else time.perf_counter()
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name="cursor")
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def snapshot(self) -> list[tuple[float, int, int]]:
        with self._lock:
            return list(self.samples)

    def last(self) -> tuple[float, int, int] | None:
        with self._lock:
            return self.samples[-1] if self.samples else None

    def _run(self) -> None:
        pt = POINT()
        ref = ctypes.byref(pt)
        prev = None
        next_at = time.perf_counter()
        while not self._stop.is_set():
            now = time.perf_counter()
            if now < next_at:
                time.sleep(min(self.interval / 4, max(0.0, next_at - now)))
                continue
            next_at = now + self.interval
            if not user32.GetCursorPos(ref):
                continue
            cur = (pt.x, pt.y)
            if cur != prev:
                with self._lock:
                    self.samples.append((now - self._t0, pt.x, pt.y))
                prev = cur

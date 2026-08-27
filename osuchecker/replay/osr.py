"""Reads .osr files from osu!stable and exported osu!lazer replays.

A frame is (time delta, x, y, keys) with the bitmask M1=1, M2=2, K1=4,
K2=8, Smoke=16. Stable sets K1/K2 and mirrors them into M1/M2, while the
lazer legacy export never sets K1/K2 at all, so the channels are chosen
from the bits a replay actually uses.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

K1_BIT, K2_BIT = 4, 8
M1_BIT, M2_BIT = 1, 2


@dataclass
class KeyEvent:
    """One key press in the replay, in map time milliseconds."""
    key: str
    press: float
    release: float
    press_prev: float
    release_prev: float

    @property
    def hold(self) -> float:
        return self.release - self.press

    @property
    def press_uncertainty(self) -> float:
        """Replay resolution at the moment of this press."""
        return self.press - self.press_prev


@dataclass
class ParsedReplay:
    path: Path
    source: str = "stable"
    mode: int = 0
    mods: int = 0
    beatmap_hash: str = ""
    username: str = ""
    count_300: int = 0
    count_100: int = 0
    count_50: int = 0
    count_miss: int = 0
    max_combo: int = 0
    score: int = 0
    game_version: int = 0
    key_channels: tuple[str, str] = ("K1", "K2")
    frames: list[tuple[float, float, float, int]] = field(default_factory=list)
    key_events: list[KeyEvent] = field(default_factory=list)

    @property
    def frame_rate(self) -> float:
        """Median replay frame rate in Hz, the limit of its precision."""
        if len(self.frames) < 10:
            return 0.0
        deltas = sorted(
            self.frames[i][0] - self.frames[i - 1][0]
            for i in range(1, len(self.frames))
            if 0 < self.frames[i][0] - self.frames[i - 1][0] < 100
        )
        if not deltas:
            return 0.0
        med = deltas[len(deltas) // 2]
        return 1000.0 / med if med > 0 else 0.0


def _extract_key_events(frames, bit: int, name: str) -> list[KeyEvent]:
    events: list[KeyEvent] = []
    prev_down = False
    prev_t = frames[0][0] if frames else 0.0
    press_t = press_prev_t = 0.0
    for t, _x, _y, keys in frames:
        down = bool(keys & bit)
        if down and not prev_down:
            press_t, press_prev_t = t, prev_t
        elif not down and prev_down:
            events.append(KeyEvent(name, press_t, t, press_prev_t, prev_t))
        prev_down = down
        prev_t = t
    if prev_down:
        events.append(KeyEvent(name, press_t, prev_t, press_prev_t, prev_t))
    return events


def parse_replay(path: str | Path) -> ParsedReplay:
    from osrparse import Replay

    path = Path(path)
    r = Replay.from_path(str(path))

    out = ParsedReplay(path=path)
    out.mode = int(getattr(r.mode, "value", r.mode) or 0)
    out.mods = int(getattr(r.mods, "value", r.mods) or 0)
    out.beatmap_hash = r.beatmap_hash or ""
    out.username = r.username or ""
    out.count_300 = r.count_300
    out.count_100 = r.count_100
    out.count_50 = r.count_50
    out.count_miss = r.count_miss
    out.max_combo = r.max_combo
    out.score = r.score
    out.game_version = int(r.game_version or 0)
    out.source = "lazer" if out.game_version >= 30000000 else "stable"

    t = 0.0
    frames: list[tuple[float, float, float, int]] = []
    for ev in r.replay_data or []:
        delta = float(getattr(ev, "time_delta", 0))
        if delta == -12345:
            continue
        t += delta
        frames.append((t, float(getattr(ev, "x", 0.0) or 0.0),
                       float(getattr(ev, "y", 0.0) or 0.0),
                       int(getattr(ev, "keys", 0) or 0)))
    frames.sort(key=lambda f: f[0])
    out.frames = frames

    used = 0
    for _t, _x, _y, k in frames:
        used |= k
    if used & (K1_BIT | K2_BIT):
        left_bit, right_bit = K1_BIT, K2_BIT
        out.key_channels = ("K1", "K2")
    else:
        left_bit, right_bit = M1_BIT, M2_BIT
        out.key_channels = ("M1", "M2")

    for bit, name in ((left_bit, "left"), (right_bit, "right")):
        out.key_events.extend(_extract_key_events(frames, bit, name))

    out.key_events.sort(key=lambda e: e.press)
    return out

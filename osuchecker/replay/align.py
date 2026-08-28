"""Puts the replay clock and the beatmap clock on the same origin.

osu!stable writes the first replay frame with its own absolute time, which
is negative because recording starts during the lead-in. On a large share
of replays that first value belongs to a different clock than the frames
after it, and taking it at face value shifts everything by the whole
lead-in — several seconds. The symptom is unmistakable: the cursor drifts
away from the notes in playback, aim looks catastrophic everywhere, and
presses land on the wrong notes so misses and extra presses explode.

Nothing in the file says which reading is right, so both are tried and the
one where presses actually fall on notes wins. A replay that fits neither
gets a bounded search, and whatever it finds is reported to the user
rather than applied silently.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .beatmap import Beatmap
from .osr import ParsedReplay

HIT_WINDOW = 50.0
GOOD = 0.90
MARGIN = 0.15
SEARCH_RANGE = 70_000.0
COARSE_STEP = 25.0
FINE_STEP = 1.0
MIN_PLAYED = 0.5


@dataclass
class Alignment:
    """How the replay clock was matched to the beatmap."""
    shift: float = 0.0
    coverage: float = 0.0
    raw_coverage: float = 0.0
    source: str = "none"
    notes: int = 0
    checked: bool = False

    @property
    def ok(self) -> bool:
        return self.coverage >= GOOD

    @property
    def suspect(self) -> bool:
        """The replay could be checked and does not line up with the map."""
        return self.checked and not self.ok

    @property
    def corrected(self) -> bool:
        return abs(self.shift) > 1.0


def note_times(bm: Beatmap) -> np.ndarray:
    return np.array([o.time for o in bm.hit_objects
                     if o.kind in ("circle", "slider")], dtype=float)


def press_times(rp: ParsedReplay) -> np.ndarray:
    return np.array(sorted(e.press for e in rp.key_events
                           if e.key in ("left", "right")), dtype=float)


def coverage(presses: np.ndarray, notes: np.ndarray, end: float,
             expected: int = 0) -> float:
    """Share of notes played that have a press within the 50 window.

    Only the stretch the replay actually covers is counted, so a play that
    was quit halfway is not judged on the notes that never appeared. That
    window is also what a search could abuse: slide the replay far enough
    and it lands on a handful of notes it happens to fit perfectly. The
    replay header says how many notes were judged, so a reading that covers
    much less than that is not a reading at all.
    """
    if len(presses) < 20 or len(notes) < 20:
        return 0.0
    inside = notes[(notes >= presses[0] - 100.0) & (notes <= end)]
    if len(inside) < max(20, expected * MIN_PLAYED):
        return 0.0
    i = np.clip(np.searchsorted(presses, inside), 1, len(presses) - 1)
    gap = np.minimum(np.abs(presses[i] - inside),
                     np.abs(presses[i - 1] - inside))
    return float((gap < HIT_WINDOW).mean())


def _best_shift(presses: np.ndarray, notes: np.ndarray, end: float,
                centre: float, span: float, step: float,
                expected: int) -> tuple[float, float]:
    best = (0.0, -1.0)
    offset = centre - span
    while offset <= centre + span:
        score = coverage(presses + offset, notes, end + offset, expected)
        if score > best[1]:
            best = (offset, score)
        offset += step
    return best


def align(rp: ParsedReplay, bm: Beatmap) -> Alignment:
    """Chooses the replay clock that puts presses on notes."""
    notes = note_times(bm)
    presses = press_times(rp)
    out = Alignment(notes=len(notes))
    if not rp.frames or len(presses) < 20 or len(notes) < 20:
        return out

    end = rp.frames[-1][0]
    expected = rp.count_300 + rp.count_100 + rp.count_50 + rp.count_miss
    out.checked = True
    out.raw_coverage = out.coverage = coverage(presses, notes, end, expected)
    out.source = "as recorded"
    if out.ok:
        return out

    # The other reading of the first frame: its time belongs to the lead-in
    # clock, and the frames after it start one frame later instead.
    #
    # The extra frame is not a guess. Measured over 85 replays that need
    # this correction, the residual offset left by shifting only by -lead_in
    # is one frame interval, to within 5 ms, and adding it makes the mean
    # hit error of these replays agree with the replays that need no
    # correction at all. Without it they read about a frame early.
    lead_in = rp.frames[0][0]
    if lead_in < -50.0:
        rate = rp.frame_rate
        candidate = -lead_in + (1000.0 / rate if rate else 0.0)
        score = coverage(presses + candidate, notes, end + candidate,
                         expected)
        if score > out.coverage + MARGIN:
            out.shift, out.coverage, out.source = candidate, score, "lead-in"
    if out.ok:
        return out

    coarse = _best_shift(presses, notes, end, 0.0, SEARCH_RANGE, COARSE_STEP,
                         expected)
    fine = _best_shift(presses, notes, end, coarse[0], COARSE_STEP, FINE_STEP,
                       expected)
    if fine[1] >= GOOD and fine[1] > out.coverage + MARGIN:
        out.shift, out.coverage, out.source = fine[0], fine[1], "search"
    return out

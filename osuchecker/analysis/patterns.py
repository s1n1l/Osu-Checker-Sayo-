"""Rhythm patterns for the trainer, and judging presses against them.

Holding one endless tempo trains stamina and nothing else. A map is made
of bursts, doubles, triples and the occasional long stream, and the hard
part is rarely the speed itself -- it is starting a burst on time after a
gap, and not carrying the last note of one run into the next.

So the trainer builds a rhythm out of runs separated by rests, and judges
presses against those note times the way the game does. The error on the
first note of a run is kept apart from the rest, because that is the
number that says whether you can enter a burst cleanly.

Everything here is plain arithmetic on millisecond timestamps: no Qt, no
device, so it can be checked directly.
"""
from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field

# A quarter-note stream at a given BPM means four presses per beat.
TAPS_PER_BEAT = 4


def tap_interval(bpm: float) -> float:
    return 15000.0 / bpm


def beat_interval(bpm: float) -> float:
    return 60000.0 / bpm


@dataclass(frozen=True)
class Pattern:
    """A repeating shape: runs of notes separated by rests."""
    key: str
    runs: tuple[int, ...]
    gap_beats: float
    shuffle: bool = False

    @property
    def name_key(self) -> str:
        return f"trn.pat.{self.key}"

    @property
    def hint_key(self) -> str:
        return f"trn.pat.{self.key}_hint"


# Ordered as they appear in the drop-down: steady first, hardest last.
PATTERNS: tuple[Pattern, ...] = (
    Pattern("stream", (0,), 0.0),
    Pattern("long", (16,), 2.0),
    Pattern("burst", (5, 7, 5, 9), 1.5, shuffle=True),
    Pattern("triple", (3,), 1.0),
    Pattern("double", (2,), 1.0),
    Pattern("mixed", (1, 2, 3, 4, 6, 8), 1.5, shuffle=True),
)
BY_KEY = {p.key: p for p in PATTERNS}
DEFAULT = "stream"


def build(pattern: Pattern, bpm: float, seconds: float, start: float = 0.0,
          seed: int | None = None) -> tuple[list[float], set[int]]:
    """Note times in milliseconds, and the indexes that open a run.

    A continuous stream is one run with no rest, which is what the trainer
    did before patterns existed.
    """
    gap = tap_interval(bpm)
    end = start + seconds * 1000.0
    times: list[float] = []
    openers: set[int] = set()
    rng = random.Random(seed)
    order = list(pattern.runs)
    at = start
    i = 0
    while at < end:
        length = order[i % len(order)] if not pattern.shuffle else rng.choice(order)
        i += 1
        if length <= 0:                      # continuous
            while at < end:
                if not times:
                    openers.add(0)
                times.append(at)
                at += gap
            break
        openers.add(len(times))
        for _ in range(length):
            if at >= end:
                break
            times.append(at)
            at += gap
        # The rest is measured from the last note of the run, and the note
        # that would have followed it is already one gap away.
        at += pattern.gap_beats * beat_interval(bpm) - gap
    return times, openers


@dataclass
class PatternResult:
    """How a set of presses lined up with the notes that were asked for."""
    errors: list[float] = field(default_factory=list)
    opener_errors: list[float] = field(default_factory=list)
    body_errors: list[float] = field(default_factory=list)
    matched: dict[int, float] = field(default_factory=dict)
    misses: int = 0
    extras: int = 0
    notes: int = 0

    @property
    def hits(self) -> int:
        return len(self.errors)

    @property
    def mean_error(self) -> float:
        return statistics.mean(self.errors) if self.errors else 0.0

    @property
    def ur(self) -> float:
        return statistics.pstdev(self.errors) * 10 if len(self.errors) > 1 else 0.0

    @property
    def accuracy(self) -> float:
        return self.hits / self.notes if self.notes else 0.0

    @property
    def opener_gap(self) -> float:
        """How much later a run is started than it is carried.

        Positive means the first note of a burst lands later than the rest
        of it -- entering late, then catching up.
        """
        if len(self.opener_errors) < 3 or len(self.body_errors) < 3:
            return 0.0
        return (statistics.mean(self.opener_errors)
                - statistics.mean(self.body_errors))


def judge(notes: list[float], openers: set[int], presses: list[float],
          window: float) -> PatternResult:
    """Matches presses to notes, nearest first, one press per note.

    Walking both lists in order is enough: both are sorted, and a press
    can only belong to the note it is closest to.
    """
    out = PatternResult(notes=len(notes))
    used = [False] * len(presses)
    j = 0
    for index, note in enumerate(notes):
        while j < len(presses) and presses[j] < note - window:
            j += 1
        best = -1
        best_gap = window
        k = j
        while k < len(presses) and presses[k] <= note + window:
            if not used[k]:
                gap = abs(presses[k] - note)
                if gap < best_gap:
                    best, best_gap = k, gap
            k += 1
        if best < 0:
            out.misses += 1
            continue
        used[best] = True
        error = presses[best] - note
        out.errors.append(error)
        out.matched[index] = error
        (out.opener_errors if index in openers else out.body_errors).append(error)
    out.extras = sum(1 for taken in used if not taken)
    return out

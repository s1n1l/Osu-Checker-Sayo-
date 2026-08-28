"""Extended tapping metrics: rhythm of the hands rather than hit accuracy.

Hit error says how close a press was to a note. These numbers describe the
press itself: how the hands alternate, how long keys are held, how fast a
tempo the hands actually sustain, and how that decays over a map.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from ..replay.osr import ParsedReplay
from .judge import JudgeResult
from .streams import bpm_from_gap

SUSTAIN_PRESSES = 16
ROLL_WINDOW = 12


@dataclass
class TapStats:
    intervals: list[float] = field(default_factory=list)
    holds: list[float] = field(default_factory=list)
    holds_left: list[float] = field(default_factory=list)
    holds_right: list[float] = field(default_factory=list)
    same_hand_runs: dict[int, int] = field(default_factory=dict)
    alternation: float = 0.0
    max_sustained_bpm: float = 0.0
    rolling: list[tuple[float, float, float]] = field(default_factory=list)
    fast_repeats: int = 0


    @property
    def median_hold(self) -> float:
        return statistics.median(self.holds) if self.holds else 0.0

    @property
    def hold_spread(self) -> float:
        return statistics.pstdev(self.holds) if len(self.holds) > 1 else 0.0

    @property
    def median_interval(self) -> float:
        return statistics.median(self.intervals) if self.intervals else 0.0

    @property
    def hand_hold_gap(self) -> float:
        if not self.holds_left or not self.holds_right:
            return 0.0
        return statistics.median(self.holds_left) - statistics.median(self.holds_right)

    @property
    def single_tap_share(self) -> float:
        total = sum(count for _, count in self.same_hand_runs.items())
        if not total:
            return 0.0
        singles = sum(count for length, count in self.same_hand_runs.items()
                      if length >= 2)
        return singles / total

    @property
    def fatigue(self) -> float:
        """UR growth from the first third of the map to the last.

        Only windows at stream tempo are counted. Comparing raw tempo instead
        would measure how the map is built, not how the hand holds up.
        """
        fast = [r for r in self.rolling if r[1] >= 140.0 and r[2] > 0]
        if len(fast) < 9:
            return 0.0
        third = len(fast) // 3
        early = statistics.median(r[2] for r in fast[:third])
        late = statistics.median(r[2] for r in fast[-third:])
        return late - early


def analyse_tapping(rp: ParsedReplay, res: JudgeResult) -> TapStats:
    stats = TapStats()
    presses = sorted([e for e in rp.key_events if e.key in ("left", "right")],
                     key=lambda e: e.press)
    if len(presses) < 4:
        return stats

    for event in presses:
        hold = event.hold
        if 0 <= hold < 2000:
            stats.holds.append(hold)
            if event.key == "left":
                stats.holds_left.append(hold)
            else:
                stats.holds_right.append(hold)

    switches = 0
    run_length = 1
    for i in range(1, len(presses)):
        gap = presses[i].press - presses[i - 1].press
        if 0 < gap < 1000:
            stats.intervals.append(gap)
        if gap < 45 and presses[i].key == presses[i - 1].key:
            stats.fast_repeats += 1
        if presses[i].key != presses[i - 1].key:
            switches += 1
            stats.same_hand_runs[run_length] = \
                stats.same_hand_runs.get(run_length, 0) + 1
            run_length = 1
        else:
            run_length += 1
    stats.same_hand_runs[run_length] = stats.same_hand_runs.get(run_length, 0) + 1
    stats.alternation = switches / (len(presses) - 1)

    times = [e.press for e in presses]
    best = 0.0
    for i in range(len(times) - SUSTAIN_PRESSES):
        span = times[i + SUSTAIN_PRESSES] - times[i]
        if span <= 0:
            continue
        bpm = bpm_from_gap(span / SUSTAIN_PRESSES)
        best = max(best, bpm)
    stats.max_sustained_bpm = best

    errors = {j.press_time: j.error for j in res.judgements
              if j.error is not None and j.press_time is not None}
    for i in range(0, len(times) - ROLL_WINDOW, ROLL_WINDOW // 2):
        window = times[i:i + ROLL_WINDOW]
        span = window[-1] - window[0]
        if span <= 0:
            continue
        bpm = bpm_from_gap(span / (len(window) - 1))
        local = [errors[x] for x in window if x in errors]
        ur = statistics.pstdev(local) * 10 if len(local) > 1 else 0.0
        stats.rolling.append((window[0], bpm, ur))

    return stats


def interval_histogram(stats: TapStats, bins: int = 60,
                       limit: float = 400.0) -> tuple[list[float], list[int]]:
    if not stats.intervals:
        return [], []
    width = limit / bins
    counts = [0] * bins
    for value in stats.intervals:
        if 0 <= value < limit:
            counts[int(value / width)] += 1
    centers = [(i + 0.5) * width for i in range(bins)]
    return centers, counts

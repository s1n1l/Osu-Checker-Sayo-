"""Splits a play into sections to tell overstreaming from lack of speed.

Two different things are measured inside one stream: drift, meaning the
error growing from the start of the stream to its end, and extra presses.
Both show up as 100s and misses in game but call for opposite fixes.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from ..replay.beatmap import Beatmap
from .judge import JudgeResult, JUDGE_MISS


def bpm_from_gap(gap_ms: float) -> float:
    """BPM of 1/4 notes spaced this many milliseconds apart."""
    return 15000.0 / gap_ms if gap_ms > 0 else 0.0


@dataclass
class Section:
    start: float
    end: float
    n_notes: int
    gap: float
    bpm: float
    errors: list[float] = field(default_factory=list)
    misses: int = 0
    extras: int = 0
    drift: float = 0.0
    intervals: list[float] = field(default_factory=list)

    @property
    def mean_error(self) -> float:
        return statistics.mean(self.errors) if self.errors else 0.0

    @property
    def ur(self) -> float:
        return statistics.pstdev(self.errors) * 10 if len(self.errors) > 1 else 0.0


def find_sections(bm: Beatmap, min_notes: int = 5,
                  max_gap: float = 200.0) -> list[tuple[int, int, float]]:
    """Finds runs of consecutive notes with a steady interval.

    Returns (first index, last index, median gap).
    """
    objs = [o for o in bm.hit_objects if o.kind in ("circle", "slider")]
    sections: list[tuple[int, int, float]] = []
    i = 0
    while i < len(objs) - 1:
        gaps = []
        j = i
        while j < len(objs) - 1:
            g = objs[j + 1].time - objs[j].time
            if g > max_gap or g <= 0:
                break
            if gaps and abs(g - gaps[0]) > gaps[0] * 0.25:
                break
            gaps.append(g)
            j += 1
        if len(gaps) + 1 >= min_notes:
            sections.append((i, j, statistics.median(gaps)))
            i = j
        else:
            i += 1
    return sections


def analyse_sections(bm: Beatmap, res: JudgeResult) -> list[Section]:
    objs = [o for o in bm.hit_objects if o.kind in ("circle", "slider")]
    by_index = {j.index: j for j in res.judgements}
    out: list[Section] = []

    for i0, i1, gap in find_sections(bm):
        sec = Section(start=objs[i0].time, end=objs[i1].time,
                      n_notes=i1 - i0 + 1, gap=gap, bpm=bpm_from_gap(gap))
        press_times = []
        for idx in range(i0, i1 + 1):
            j = by_index.get(idx)
            if j is None:
                continue
            if j.judgement == JUDGE_MISS:
                sec.misses += 1
            elif j.error is not None:
                sec.errors.append(j.error)
                press_times.append(j.press_time)
        sec.extras = sum(1 for e in res.extras if sec.start <= e.time <= sec.end)
        press_times.sort()
        sec.intervals = [press_times[k] - press_times[k - 1]
                         for k in range(1, len(press_times))]
        if len(sec.errors) >= 6:
            third = max(2, len(sec.errors) // 3)
            sec.drift = statistics.mean(sec.errors[-third:]) - statistics.mean(sec.errors[:third])
        out.append(sec)
    return out


@dataclass
class BpmBucket:
    bpm: float
    n_notes: int = 0
    n_sections: int = 0
    errors: list[float] = field(default_factory=list)
    misses: int = 0
    extras: int = 0
    drifts: list[float] = field(default_factory=list)

    @property
    def mean_error(self) -> float:
        return statistics.mean(self.errors) if self.errors else 0.0

    @property
    def ur(self) -> float:
        return statistics.pstdev(self.errors) * 10 if len(self.errors) > 1 else 0.0

    @property
    def miss_rate(self) -> float:
        return self.misses / self.n_notes if self.n_notes else 0.0

    @property
    def extra_rate(self) -> float:
        return self.extras / self.n_notes if self.n_notes else 0.0

    @property
    def mean_drift(self) -> float:
        return statistics.mean(self.drifts) if self.drifts else 0.0


def bucket_by_bpm(sections: list[Section], step: float = 10.0) -> list[BpmBucket]:
    buckets: dict[float, BpmBucket] = {}
    for s in sections:
        key = round(s.bpm / step) * step
        b = buckets.setdefault(key, BpmBucket(bpm=key))
        b.n_notes += s.n_notes
        b.n_sections += 1
        b.errors.extend(s.errors)
        b.misses += s.misses
        b.extras += s.extras
        if s.n_notes >= 6:
            b.drifts.append(s.drift)
    return [buckets[k] for k in sorted(buckets)]

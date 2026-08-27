"""Finds the specific stretches of a map where the score was lost.

Map-wide averages say nothing about what to do next, so the map is cut into
short windows and every bad window is described with a cause.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from ..i18n import t
from ..replay.beatmap import Beatmap
from .aim import AimResult
from .judge import JUDGE_100, JUDGE_50, JUDGE_MISS, JudgeResult
from .streams import Section, bpm_from_gap

WINDOW_MS = 2500.0
CAUSE_LATE = "late"
CAUSE_EARLY = "early"
CAUSE_SCATTER = "scatter"
CAUSE_AIM = "aim"
CAUSE_MIXED = "mixed"

AIM_SPREAD_LIMIT = 0.62
AIM_EDGE_LIMIT = 0.28
DRIFT_LIMIT = 10.0
LATE_LIMIT = 5.0
EARLY_LIMIT = -8.0
SCATTER_UR_LIMIT = 220.0


def mmss(ms: float) -> str:
    s = int(ms / 1000)
    return f"{s // 60:02d}:{s % 60:02d}"


@dataclass
class Episode:
    start: float
    end: float
    n_notes: int = 0
    misses: int = 0
    hundreds: int = 0
    fifties: int = 0
    errors: list[float] = field(default_factory=list)
    bpm: float = 0.0
    drift: float = 0.0
    early_mean: float = 0.0
    late_mean: float = 0.0
    aim_spread: float = 0.0
    aim_edge: float = 0.0
    cause: str = CAUSE_MIXED
    score: float = 0.0

    @property
    def mean_error(self) -> float:
        return statistics.mean(self.errors) if self.errors else 0.0

    @property
    def ur(self) -> float:
        return statistics.pstdev(self.errors) * 10 if len(self.errors) > 1 else 0.0

    @property
    def time_label(self) -> str:
        return f"{mmss(self.start)}–{mmss(self.end)}"

    @property
    def cause_label(self) -> str:
        return t(f"ep.cause.{self.cause}")

    @property
    def loss_label(self) -> str:
        parts = []
        if self.misses:
            parts.append(t("ep.miss", n=self.misses))
        if self.hundreds:
            parts.append(t("ep.hundred", n=self.hundreds))
        if self.fifties:
            parts.append(t("ep.fifty", n=self.fifties))
        return ", ".join(parts) if parts else t("ep.none")

    @property
    def what(self) -> str:
        if self.cause == CAUSE_LATE:
            return t("ep.what.late", early=self.early_mean, late=self.late_mean)
        if self.cause == CAUSE_EARLY:
            return t("ep.what.early", mean=self.mean_error)
        if self.cause == CAUSE_SCATTER:
            return t("ep.what.scatter", mean=self.mean_error, ur=self.ur)
        if self.cause == CAUSE_AIM:
            return t("ep.what.aim", spread=self.aim_spread,
                     edge=self.aim_edge * 100)
        return t("ep.what.mixed", mean=self.mean_error, ur=self.ur)

    def describe(self) -> str:
        return (f"{self.time_label}  ·  {self.n_notes}  ·  "
                f"{self.loss_label}  ·  {self.what}")


def find_episodes(bm: Beatmap, res: JudgeResult, sections: list[Section],
                  aim: AimResult | None = None,
                  limit: int = 12) -> list[Episode]:
    judged = sorted([j for j in res.judgements if j.obj is not None],
                    key=lambda j: j.obj.time)
    if not judged:
        return []

    aim_by_index = {h.index: h for h in (aim.hits if aim else [])}
    w300 = res.windows.get("300", 30.0)

    episodes: list[Episode] = []
    i = 0
    while i < len(judged):
        t0 = judged[i].obj.time
        ep = Episode(start=t0, end=t0 + WINDOW_MS)
        spreads, edges = [], 0
        j = i
        while j < len(judged) and judged[j].obj.time < t0 + WINDOW_MS:
            g = judged[j]
            ep.n_notes += 1
            if g.judgement == JUDGE_MISS:
                ep.misses += 1
            elif g.judgement == JUDGE_100:
                ep.hundreds += 1
            elif g.judgement == JUDGE_50:
                ep.fifties += 1
            if g.error is not None:
                ep.errors.append(g.error)
            h = aim_by_index.get(g.index)
            if h is not None:
                spreads.append(h.dist_norm)
                if h.dist_norm > 0.75:
                    edges += 1
            j += 1
        ep.end = judged[j - 1].obj.time
        if spreads:
            ep.aim_spread = statistics.mean(spreads)
            ep.aim_edge = edges / len(spreads)

        gaps = [judged[k].obj.time - judged[k - 1].obj.time
                for k in range(i + 1, j)]
        gaps = [g for g in gaps if 0 < g < 400]
        if gaps:
            ep.bpm = bpm_from_gap(statistics.median(gaps))

        if len(ep.errors) >= 6:
            third = max(2, len(ep.errors) // 3)
            ep.early_mean = statistics.mean(ep.errors[:third])
            ep.late_mean = statistics.mean(ep.errors[-third:])
            ep.drift = ep.late_mean - ep.early_mean

        ep.score = ep.misses * 3.0 + ep.hundreds * 1.0 + ep.fifties * 1.5
        if ep.n_notes >= 4 and ep.score > 0:
            episodes.append(ep)
        i = j if j > i else i + 1

    for ep in episodes:
        if ep.aim_spread and (ep.aim_spread > AIM_SPREAD_LIMIT
                              or ep.aim_edge > AIM_EDGE_LIMIT):
            ep.cause = CAUSE_AIM
        elif ep.drift >= DRIFT_LIMIT and ep.late_mean > LATE_LIMIT:
            ep.cause = CAUSE_LATE
        elif ep.mean_error <= EARLY_LIMIT:
            ep.cause = CAUSE_EARLY
        elif (ep.ur > SCATTER_UR_LIMIT
              and abs(ep.mean_error) < w300 * 0.4):
            ep.cause = CAUSE_SCATTER
        else:
            ep.cause = CAUSE_MIXED

    episodes.sort(key=lambda e: -e.score)
    return episodes[:limit]


def cause_summary(episodes: list[Episode]) -> dict[str, int]:
    out: dict[str, int] = {}
    for e in episodes:
        out[e.cause] = out.get(e.cause, 0) + 1
    return out

"""Builds a training plan from the measured numbers.

Every exercise carries a criterion this app can verify on the next replay.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..i18n import t
from ..paths import data_file
from ..replay.beatmap import parse_beatmap
from .aim import AimResult
from .episodes import CAUSE_EARLY, CAUSE_SCATTER, Episode
from .streams import BpmBucket, bpm_from_gap, find_sections

CACHE = data_file("map_profiles.json")


@dataclass
class Exercise:
    priority: int
    title_key: str
    why_key: str
    how_key: str
    check_key: str
    params: dict = field(default_factory=dict)
    target_bpm: float = 0.0

    @property
    def title(self) -> str:
        return t(self.title_key, **self.params)

    @property
    def why(self) -> str:
        return t(self.why_key, **self.params)

    @property
    def how(self) -> str:
        return t(self.how_key, **self.params)

    @property
    def check(self) -> str:
        return t(self.check_key, **self.params)


def build_plan(buckets: list[BpmBucket], episodes: list[Episode],
               aim: AimResult | None, hand_gap: float = 0.0) -> list[Exercise]:
    plan: list[Exercise] = []

    weak = [b for b in buckets
            if b.bpm >= 140 and b.n_notes >= 40 and b.mean_drift >= 8]
    if weak:
        worst = max(weak, key=lambda b: b.mean_drift)
        plan.append(Exercise(
            priority=1,
            title_key="tr.ex.stream.title",
            why_key="tr.ex.stream.why",
            how_key="tr.ex.stream.how",
            check_key="tr.ex.stream.check",
            target_bpm=worst.bpm,
            params={"bpm": worst.bpm, "drift": worst.mean_drift,
                    "notes": worst.n_notes, "ur": worst.ur,
                    "base": round(worst.bpm * 0.9 / 5) * 5}))

    over = [b for b in buckets
            if b.bpm < 140 and b.n_notes >= 40 and b.extra_rate >= 0.02]
    if over:
        worst = max(over, key=lambda b: b.extra_rate)
        plan.append(Exercise(
            priority=2,
            title_key="tr.ex.overstream.title",
            why_key="tr.ex.overstream.why",
            how_key="tr.ex.overstream.how",
            check_key="tr.ex.overstream.check",
            target_bpm=worst.bpm,
            params={"bpm": worst.bpm, "extra": worst.extra_rate * 100,
                    "drift": worst.mean_drift}))

    if aim and aim.hits:
        big = [b for b in aim.by_jump_size() if b["lo"] >= 120]
        bad = [b for b in big
               if b["edge_rate"] > 0.12 or b["overshoot_rate"] > 0.30]
        if bad:
            b = max(bad, key=lambda x: x["edge_rate"])
            plan.append(Exercise(
                priority=2,
                title_key="tr.ex.aim_jump.title",
                why_key="tr.ex.aim_jump.why",
                how_key="tr.ex.aim_jump.how",
                check_key="tr.ex.aim_jump.check",
                params={"lo": b["lo"], "edge": b["edge_rate"] * 100,
                        "over": b["overshoot"], "radius": aim.radius}))
        elif aim.overshoot_rate > 0.30:
            plan.append(Exercise(
                priority=3,
                title_key="tr.ex.aim_brake.title",
                why_key="tr.ex.aim_brake.why",
                how_key="tr.ex.aim_brake.how",
                check_key="tr.ex.aim_brake.check",
                params={"pct": aim.overshoot_rate * 100,
                        "px": aim.mean_overshoot}))

    if abs(hand_gap) >= 4:
        side = "left" if hand_gap > 0 else "right"
        plan.append(Exercise(
            priority=3,
            title_key=f"tr.ex.hands.title_{side}",
            why_key="tr.ex.hands.why",
            how_key=f"tr.ex.hands.how_{side}",
            check_key="tr.ex.hands.check",
            params={"gap": abs(hand_gap)}))

    causes: dict[str, int] = {}
    for e in episodes:
        causes[e.cause] = causes.get(e.cause, 0) + 1

    if causes.get(CAUSE_SCATTER, 0) >= 3:
        plan.append(Exercise(
            priority=3,
            title_key="tr.ex.scatter.title",
            why_key="tr.ex.scatter.why",
            how_key="tr.ex.scatter.how",
            check_key="tr.ex.scatter.check",
            params={"n": causes[CAUSE_SCATTER]}))

    if causes.get(CAUSE_EARLY, 0) >= 3:
        plan.append(Exercise(
            priority=3,
            title_key="tr.ex.early.title",
            why_key="tr.ex.early.why",
            how_key="tr.ex.early.how",
            check_key="tr.ex.early.check",
            params={"n": causes[CAUSE_EARLY]}))

    plan.sort(key=lambda e: e.priority)
    return plan


@dataclass
class MapProfile:
    path: str
    title: str = ""
    version: str = ""
    cs: float = 0.0
    od: float = 0.0
    stream_bpm: float = 0.0
    stream_notes: int = 0
    total_notes: int = 0


def profile_map(path: str | Path) -> MapProfile | None:
    try:
        bm = parse_beatmap(path)
    except (OSError, ValueError):
        return None
    if bm.mode != 0 or len(bm.hit_objects) < 50:
        return None
    p = MapProfile(path=str(path), title=f"{bm.artist} - {bm.title}",
                   version=bm.version, cs=bm.cs, od=bm.od,
                   total_notes=len(bm.hit_objects))
    best = None
    for i0, i1, gap in find_sections(bm, min_notes=8, max_gap=200.0):
        n = i1 - i0 + 1
        if best is None or n > best[0]:
            best = (n, gap)
    if best:
        p.stream_notes = best[0]
        p.stream_bpm = bpm_from_gap(best[1])
    return p


def scan_maps(paths: list[str], progress=None,
              cache: str | Path = CACHE) -> list[MapProfile]:
    cache = Path(cache)
    known: dict[str, dict] = {}
    if cache.exists():
        try:
            known = {d["path"]: d for d in
                     json.loads(cache.read_text(encoding="utf-8"))}
        except (json.JSONDecodeError, OSError, KeyError):
            known = {}

    out: list[MapProfile] = []
    todo = [p for p in paths if p not in known]
    for i, p in enumerate(todo):
        if progress and i % 100 == 0:
            progress(i, len(todo), Path(p).parent.name[:40])
        prof = profile_map(p)
        if prof:
            known[p] = prof.__dict__
    for p in paths:
        d = known.get(p)
        if d:
            out.append(MapProfile(**d))
    cache.write_text(json.dumps(list(known.values())), encoding="utf-8")
    return out


def find_practice_maps(profiles: list[MapProfile], bpm: float,
                       tol: float = 6.0, min_notes: int = 16,
                       limit: int = 25) -> list[MapProfile]:
    sel = [p for p in profiles
           if abs(p.stream_bpm - bpm) <= tol and p.stream_notes >= min_notes]
    sel.sort(key=lambda p: -p.stream_notes)
    return sel[:limit]

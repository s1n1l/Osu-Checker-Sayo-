"""Matches replay key presses against the notes of a beatmap.

The model approximates osu!: a press judges the first unjudged note inside
the 50 window. Notes the clock ran past become misses, and presses with no
note nearby are counted as extras.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..replay.beatmap import Beatmap, HitObject
from ..replay.osr import ParsedReplay

JUDGE_300, JUDGE_100, JUDGE_50, JUDGE_MISS = "300", "100", "50", "miss"


@dataclass
class Judgement:
    obj: HitObject
    index: int
    judgement: str
    error: float | None = None
    key: str | None = None
    press_time: float | None = None
    uncertainty: float = 0.0


@dataclass
class ExtraPress:
    key: str
    time: float
    nearest_obj_dt: float | None
    since_prev_press: float | None


@dataclass
class JudgeResult:
    judgements: list[Judgement] = field(default_factory=list)
    extras: list[ExtraPress] = field(default_factory=list)
    windows: dict[str, float] = field(default_factory=dict)
    rate: float = 1.0
    spinner_presses: int = 0

    def counts(self) -> dict[str, int]:
        c = {JUDGE_300: 0, JUDGE_100: 0, JUDGE_50: 0, JUDGE_MISS: 0}
        for j in self.judgements:
            c[j.judgement] += 1
        return c

    def errors(self, key: str | None = None) -> list[float]:
        return [j.error for j in self.judgements
                if j.error is not None and (key is None or j.key == key)]


def judge_replay(bm: Beatmap, rp: ParsedReplay) -> JudgeResult:
    w = bm.hit_windows(rp.mods)
    res = JudgeResult(windows=w, rate=Beatmap.rate(rp.mods))

    objs = [o for o in bm.hit_objects if o.kind in ("circle", "slider")]
    spinners = [(o.time - w["50"], o.end_time + w["50"])
                for o in bm.hit_objects if o.kind == "spinner"]
    if rp.frames:
        played_until = rp.frames[-1][0] + w["50"]
        objs = [o for o in objs if o.time <= played_until]
    presses = sorted([e for e in rp.key_events if e.key in ("left", "right")],
                     key=lambda e: e.press)

    w50 = w["50"]
    ptr = 0
    last_press_by_key: dict[str, float] = {}

    for ev in presses:
        t = ev.press
        while ptr < len(objs) and objs[ptr].time + w50 < t:
            res.judgements.append(Judgement(objs[ptr], ptr, JUDGE_MISS))
            ptr += 1
        if ptr < len(objs) and t >= objs[ptr].time - w50:
            o = objs[ptr]
            err = t - o.time
            a = abs(err)
            jd = JUDGE_300 if a <= w["300"] else (JUDGE_100 if a <= w["100"] else JUDGE_50)
            res.judgements.append(Judgement(o, ptr, jd, err, ev.key, t,
                                            ev.press_uncertainty))
            ptr += 1
        elif any(lo <= t <= hi for lo, hi in spinners):
            # A spinner is spun with a key held down, so presses inside one
            # are part of playing it, not surplus taps.
            res.spinner_presses += 1
        else:
            near = None
            if objs:
                cand = min(objs, key=lambda o: abs(o.time - t))
                near = t - cand.time
            res.extras.append(ExtraPress(ev.key, t, near,
                                         t - last_press_by_key[ev.key]
                                         if ev.key in last_press_by_key else None))
        last_press_by_key[ev.key] = t

    while ptr < len(objs):
        res.judgements.append(Judgement(objs[ptr], ptr, JUDGE_MISS))
        ptr += 1

    res.judgements.sort(key=lambda j: j.index)
    return res

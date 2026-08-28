"""Aim analysis: where the cursor landed and how it travelled there.

Three effects are kept apart: a constant offset from the centre, a wide
spread around it, and overshoot past the target. Offset and spread are
read from the cursor position at the moment of the press; overshoot needs
the path between notes.

Coordinates are osu! pixels on a 512x384 field. HR mirrors the field
vertically and the replay already stores the cursor mirrored, so hit
objects are flipped instead.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field

import numpy as np

from ..replay.beatmap import MOD_EZ, MOD_HR, Beatmap
from ..replay.osr import ParsedReplay
from .judge import JUDGE_300, JUDGE_MISS, JudgeResult

PLAYFIELD_H = 384.0


def circle_radius(cs: float, mods: int = 0) -> float:
    """Circle radius in osu! pixels."""
    if mods & MOD_HR:
        cs = min(10.0, cs * 1.3)
    elif mods & MOD_EZ:
        cs = cs * 0.5
    return 54.4 - 4.48 * cs


@dataclass
class AimHit:
    index: int
    time: float
    dx: float
    dy: float
    dist: float
    dist_norm: float
    jump: float
    angle: float
    overshoot: float
    overshoot_norm: float
    speed: float = 0.0
    settle: float = 0.0
    judgement: str = JUDGE_300
    frame_blur: float = 0.0

    @property
    def outside(self) -> bool:
        """The sampled cursor position sits outside the circle."""
        return self.dist_norm > 1.0


@dataclass
class AimResult:
    radius: float = 0.0
    hits: list[AimHit] = field(default_factory=list)
    frame_ms: float = 0.0

    @property
    def outside_rate(self) -> float:
        """Share of notes whose sampled cursor sits outside the circle.

        These are the points beyond the ring on the scatter. They are not
        misses: the replay stores a cursor position every frame_ms, so the
        position used is the last one written before the press, and on a
        fast jump the cursor has already moved on by the time it is
        written again.
        """
        if not self.hits:
            return 0.0
        return sum(1 for h in self.hits if h.outside) / len(self.hits)

    @property
    def outside_blur(self) -> float:
        """How far the cursor moved per frame on the notes drawn outside.

        Quoted next to the share outside, because it is the size of the
        sampling error that put them there.
        """
        if not self.hits:
            return 0.0
        outside = [h.frame_blur for h in self.hits if h.outside]
        if outside:
            return statistics.mean(outside)
        ordered = sorted(h.frame_blur for h in self.hits)
        return ordered[int(len(ordered) * 0.9)]

    @property
    def median_dist_norm(self) -> float:
        if not self.hits:
            return 0.0
        return statistics.median(h.dist_norm for h in self.hits)

    @property
    def bias(self) -> tuple[float, float]:
        if not self.hits:
            return 0.0, 0.0
        return (statistics.mean(h.dx for h in self.hits),
                statistics.mean(h.dy for h in self.hits))

    @property
    def spread(self) -> float:
        """Mean distance from the centre, in fractions of the radius."""
        return statistics.mean(h.dist_norm for h in self.hits) if self.hits else 0.0

    @property
    def edge_rate(self) -> float:
        """Share of notes hit past 0.75 of the radius."""
        if not self.hits:
            return 0.0
        return sum(1 for h in self.hits if h.dist_norm > 0.75) / len(self.hits)

    @property
    def overshoot_rate(self) -> float:
        """Share of jumps overshooting by more than a quarter radius."""
        jumps = [h for h in self.hits if h.jump > self.radius]
        if not jumps:
            return 0.0
        return sum(1 for h in jumps if h.overshoot_norm > 0.25) / len(jumps)

    @property
    def mean_overshoot(self) -> float:
        jumps = [h for h in self.hits if h.jump > self.radius]
        return statistics.mean(h.overshoot for h in jumps) if jumps else 0.0

    @property
    def mean_speed(self) -> float:
        return statistics.mean(h.speed for h in self.hits) if self.hits else 0.0

    @property
    def median_settle(self) -> float:
        return statistics.median(h.settle for h in self.hits) if self.hits else 0.0

    @property
    def on_arrival_rate(self) -> float:
        """Share of notes clicked before the cursor had settled in the circle."""
        jumps = [h for h in self.hits if h.jump > self.radius]
        if not jumps:
            return 0.0
        return sum(1 for h in jumps if h.settle < 20.0) / len(jumps)

    def by_jump_size(self, edges=(0, 60, 120, 200, 1e9)) -> list[dict]:
        """Breakdown by jump distance."""
        out = []
        for i in range(len(edges) - 1):
            lo, hi = edges[i], edges[i + 1]
            sel = [h for h in self.hits if lo <= h.jump < hi]
            if len(sel) < 10:
                continue
            out.append({
                "lo": lo, "hi": hi, "n": len(sel),
                "spread": statistics.mean(h.dist_norm for h in sel),
                "edge_rate": sum(1 for h in sel if h.dist_norm > 0.75) / len(sel),
                "overshoot": statistics.mean(h.overshoot for h in sel),
                "overshoot_rate": sum(1 for h in sel if h.overshoot_norm > 0.25) / len(sel),
                "speed": statistics.mean(h.speed for h in sel),
                "settle": statistics.median(h.settle for h in sel),
            })
        return out

    def by_direction(self) -> list[dict]:
        """Breakdown by jump direction, eight sectors."""
        names = ["→", "↗", "↑", "↖", "←", "↙", "↓", "↘"]
        out = []
        for s in range(8):
            lo, hi = s * 45 - 22.5, s * 45 + 22.5
            sel = [h for h in self.hits
                   if h.jump > self.radius
                   and (lo % 360 <= h.angle < hi % 360
                        if lo % 360 < hi % 360
                        else h.angle >= lo % 360 or h.angle < hi % 360)]
            if len(sel) < 8:
                continue
            out.append({
                "name": names[s], "n": len(sel),
                "spread": statistics.mean(h.dist_norm for h in sel),
                "overshoot": statistics.mean(h.overshoot for h in sel),
            })
        return out


def _cursor_arrays(rp: ParsedReplay):
    t = np.array([f[0] for f in rp.frames], dtype=float)
    x = np.array([f[1] for f in rp.frames], dtype=float)
    y = np.array([f[2] for f in rp.frames], dtype=float)
    order = np.argsort(t)
    return t[order], x[order], y[order]


def analyse_aim(bm: Beatmap, rp: ParsedReplay, res: JudgeResult) -> AimResult:
    out = AimResult(radius=circle_radius(bm.cs, rp.mods))
    if len(rp.frames) < 10:
        return out

    frame_rate = rp.frame_rate
    out.frame_ms = 1000.0 / frame_rate if frame_rate else 0.0
    ct, cx, cy = _cursor_arrays(rp)
    flip = bool(rp.mods & MOD_HR)
    spinners = [(o.time, o.end_time) for o in bm.hit_objects
                if o.kind == "spinner"]

    def obj_xy(o):
        return o.x, (PLAYFIELD_H - o.y if flip else o.y)

    def in_spinner(t: float) -> bool:
        return any(lo <= t <= hi for lo, hi in spinners)

    # A spinner drags the cursor round the edge of the field, so a note
    # judged while one is running says nothing about aim.
    judged = [j for j in res.judgements
              if j.judgement != JUDGE_MISS and j.press_time is not None
              and not in_spinner(j.press_time)]
    prev_pos = None
    prev_time = None

    for j in judged:
        ox, oy = obj_xy(j.obj)
        t = j.press_time
        px = float(np.interp(t, ct, cx))
        py = float(np.interp(t, ct, cy))
        dx, dy = px - ox, py - oy
        dist = math.hypot(dx, dy)

        jump = 0.0
        angle = 0.0
        overshoot = 0.0
        if prev_pos is not None:
            jx, jy = ox - prev_pos[0], oy - prev_pos[1]
            jump = math.hypot(jx, jy)
            angle = math.degrees(math.atan2(-jy, jx)) % 360.0
            if jump > 1e-6:
                ux, uy = jx / jump, jy / jump
                lo = np.searchsorted(ct, prev_time)
                hi = np.searchsorted(ct, t)
                if hi > lo:
                    proj = ((cx[lo:hi] - prev_pos[0]) * ux
                            + (cy[lo:hi] - prev_pos[1]) * uy)
                    overshoot = max(0.0, float(proj.max()) - jump)

        # Speed across the frame the press falls in. A fixed lookback does
        # not work: at 60 Hz an 8 ms window lands inside a single frame and
        # every reading comes out as zero.
        here = int(np.clip(np.searchsorted(ct, t), 1, len(ct) - 1))
        back = here - 1
        span = ct[here] - ct[back]
        speed = 0.0
        if span > 0:
            speed = float(math.hypot(cx[here] - cx[back],
                                     cy[here] - cy[back]) / span)

        settle = 0.0
        if out.radius:
            i = int(np.searchsorted(ct, t)) - 1
            while i >= 0 and t - ct[i] < 500.0:
                if math.hypot(cx[i] - ox, cy[i] - oy) > out.radius:
                    break
                settle = t - ct[i]
                i -= 1

        out.hits.append(AimHit(
            index=j.index, time=j.obj.time, dx=dx, dy=dy, dist=dist,
            dist_norm=dist / out.radius if out.radius else 0.0,
            jump=jump, angle=angle, overshoot=overshoot,
            overshoot_norm=overshoot / out.radius if out.radius else 0.0,
            speed=speed, settle=settle, judgement=j.judgement,
            frame_blur=speed * out.frame_ms))

        prev_pos = (ox, oy)
        prev_time = t

    return out

"""Turns measured metrics into localised findings."""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from ..i18n import t
from ..replay.beatmap import Beatmap
from ..replay.osr import ParsedReplay
from .judge import JudgeResult
from .streams import BpmBucket, Section

AREA_DEVICE, AREA_TECHNIQUE, AREA_GAME = "device", "technique", "game"
DOUBLE_PRESS_MS = 45.0


@dataclass
class Finding:
    severity: str
    area: str
    title_key: str
    detail_key: str
    action_key: str = ""
    params: dict = field(default_factory=dict)
    key_params: dict = field(default_factory=dict)

    def _resolved(self) -> dict:
        out = dict(self.params)
        out.update({name: t(key) for name, key in self.key_params.items()})
        return out

    @property
    def title(self) -> str:
        return t(self.title_key, **self._resolved())

    @property
    def detail(self) -> str:
        return t(self.detail_key, **self._resolved())

    @property
    def action(self) -> str:
        return t(self.action_key, **self._resolved()) if self.action_key else ""

    @property
    def area_label(self) -> str:
        return t(f"area.{self.area}")

    @property
    def severity_label(self) -> str:
        return t(f"sev.{self.severity}")


def build_findings(bm: Beatmap, rp: ParsedReplay, res: JudgeResult,
                   sections: list[Section], buckets: list[BpmBucket],
                   device: dict | None = None) -> list[Finding]:
    out: list[Finding] = []
    all_err = res.errors()
    if not all_err:
        return [Finding("info", AREA_GAME, "find.no_data.title",
                        "find.no_data.detail")]

    mean_all = statistics.mean(all_err)
    left, right = res.errors("left"), res.errors("right")

    fps = rp.frame_rate
    if fps and fps < 200:
        out.append(Finding(
            "info", AREA_GAME, "find.fps.title", "find.fps.detail",
            "find.fps.action", {"fps": fps, "ms": 1000.0 / fps}))

    if abs(mean_all) >= 12:
        out.append(Finding(
            "medium", AREA_GAME, "find.offset.title", "find.offset.detail",
            "find.offset.action",
            {"mean": mean_all, "shift": -mean_all},
            {"direction": "find.offset.late" if mean_all > 0
                          else "find.offset.early"}))

    if len(left) > 30 and len(right) > 30:
        mean_l, mean_r = statistics.mean(left), statistics.mean(right)
        gap = mean_l - mean_r
        if abs(gap) >= 4:
            side = "left" if gap > 0 else "right"
            out.append(Finding(
                "medium", AREA_TECHNIQUE, "find.hands.title",
                f"find.hands.detail_{side}", f"find.hands.action_{side}",
                {"gap": abs(gap), "left": mean_l, "right": mean_r}))

        ur_l = statistics.pstdev(left) * 10
        ur_r = statistics.pstdev(right) * 10
        if max(ur_l, ur_r) > 0 and abs(ur_l - ur_r) / max(ur_l, ur_r) > 0.2:
            worse = "hand.left" if ur_l > ur_r else "hand.right"
            out.append(Finding(
                "info", AREA_TECHNIQUE, "find.hands_ur.title",
                "find.hands_ur.detail", "find.hands_ur.action",
                {"left": ur_l, "right": ur_r}, {"hand": worse}))

    for b in [x for x in buckets if x.bpm >= 140 and x.n_notes >= 40]:
        if b.mean_drift >= 8:
            out.append(Finding(
                "high", AREA_TECHNIQUE, "find.drift.title", "find.drift.detail",
                "find.drift.action",
                {"bpm": b.bpm, "drift": b.mean_drift, "notes": b.n_notes,
                 "ur": b.ur, "miss": b.miss_rate * 100,
                 "extra": b.extra_rate * 100}))
        elif b.extra_rate >= 0.02:
            out.append(Finding(
                "high", AREA_TECHNIQUE, "find.overstream.title",
                "find.overstream.detail", "find.overstream.action",
                {"bpm": b.bpm, "extra": b.extra_rate * 100,
                 "drift": b.mean_drift}))

    slow_extra = [b for b in buckets
                  if b.bpm < 140 and b.n_notes >= 40 and b.extra_rate >= 0.02]
    if slow_extra:
        worst = max(slow_extra, key=lambda b: b.extra_rate)
        out.append(Finding(
            "medium", AREA_TECHNIQUE, "find.slow_extras.title",
            "find.slow_extras.detail", "find.slow_extras.action",
            {"bpm": worst.bpm, "extra": worst.extra_rate * 100,
             "drift": worst.mean_drift}))

    rapid = [e for e in res.extras
             if e.since_prev_press is not None
             and e.since_prev_press < DOUBLE_PRESS_MS]
    total_presses = len(res.judgements) + len(res.extras)
    if total_presses and len(rapid) / total_presses >= 0.005:
        out.append(Finding(
            "high", AREA_DEVICE, "find.double.title", "find.double.detail",
            "find.double.action",
            {"n": len(rapid), "pct": len(rapid) / total_presses * 100}))
    else:
        out.append(Finding(
            "info", AREA_DEVICE, "find.no_double.title",
            "find.no_double.detail", "find.no_double.action",
            {"n": len(rapid), "total": total_presses}))

    if device:
        peak = device.get("peak_depth_um")
        trigger = device.get("trigger_um")
        if peak and trigger and peak < trigger * 1.3:
            out.append(Finding(
                "high", AREA_DEVICE, "find.underpress.title",
                "find.underpress.detail", "find.underpress.action",
                {"peak": peak, "trigger": trigger, "margin": peak - trigger,
                 "now": trigger / 1000.0,
                 "suggest": max(100.0, trigger * 0.6) / 1000.0}))

    order = {"high": 0, "medium": 1, "info": 2}
    out.sort(key=lambda f: order.get(f.severity, 3))
    return out

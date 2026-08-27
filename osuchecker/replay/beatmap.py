"""Parser for .osu files in osu!standard: hit objects, timing, hit windows.

Times are map times, not real time: with DT or HT real time is map time
divided by the rate. Hit windows are measured in map time and so do not
depend on the rate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

_T_CIRCLE, _T_SLIDER, _T_SPINNER, _T_HOLD = 1, 2, 8, 128

MOD_EZ, MOD_HR, MOD_DT, MOD_HT, MOD_NC = 2, 16, 64, 256, 512


@dataclass
class TimingPoint:
    time: float
    beat_length: float
    uninherited: bool


@dataclass
class HitObject:
    time: float
    end_time: float
    kind: str
    x: float
    y: float
    new_combo: bool

    @property
    def duration(self) -> float:
        return self.end_time - self.time


@dataclass
class Beatmap:
    path: Path | None = None
    mode: int = 0
    title: str = ""
    artist: str = ""
    version: str = ""
    od: float = 5.0
    ar: float = 5.0
    cs: float = 4.0
    hp: float = 5.0
    slider_multiplier: float = 1.4
    timing_points: list[TimingPoint] = field(default_factory=list)
    hit_objects: list[HitObject] = field(default_factory=list)

    def hit_windows(self, mods: int = 0) -> dict[str, float]:
        od = self.od
        if mods & MOD_HR:
            od = min(10.0, od * 1.4)
        elif mods & MOD_EZ:
            od = od * 0.5
        return {
            "300": 80.0 - 6.0 * od,
            "100": 140.0 - 8.0 * od,
            "50": 200.0 - 10.0 * od,
            "od": od,
        }

    @staticmethod
    def rate(mods: int = 0) -> float:
        """Speed multiplier: real time is map time divided by this."""
        if mods & (MOD_DT | MOD_NC):
            return 1.5
        if mods & MOD_HT:
            return 0.75
        return 1.0

    def beat_length_at(self, time: float) -> tuple[float, float]:
        """Beat length in ms and slider velocity multiplier at a given time."""
        beat = 500.0
        sv = 1.0
        for tp in self.timing_points:
            if tp.time > time + 1e-6:
                break
            if tp.uninherited:
                beat = tp.beat_length
                sv = 1.0
            else:
                sv = 100.0 / -tp.beat_length if tp.beat_length < 0 else 1.0
        return beat, sv


def _section_lines(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if line.startswith("[") and line.endswith("]"):
            cur = line[1:-1]
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def _kv(lines: list[str]) -> dict[str, str]:
    d = {}
    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def parse_beatmap(path: str | Path) -> Beatmap:
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    sections = _section_lines(text)
    bm = Beatmap(path=path)

    general = _kv(sections.get("General", []))
    bm.mode = int(general.get("Mode", 0))

    meta = _kv(sections.get("Metadata", []))
    bm.title = meta.get("Title", "")
    bm.artist = meta.get("Artist", "")
    bm.version = meta.get("Version", "")

    diff = _kv(sections.get("Difficulty", []))
    bm.od = float(diff.get("OverallDifficulty", 5))
    bm.ar = float(diff.get("ApproachRate", bm.od))
    bm.cs = float(diff.get("CircleSize", 4))
    bm.hp = float(diff.get("HPDrainRate", 5))
    bm.slider_multiplier = float(diff.get("SliderMultiplier", 1.4))

    for line in sections.get("TimingPoints", []):
        p = line.split(",")
        if len(p) < 2:
            continue
        try:
            t = float(p[0])
            bl = float(p[1])
        except ValueError:
            continue
        uninherited = True if len(p) < 7 else p[6].strip() == "1"
        bm.timing_points.append(TimingPoint(t, bl, uninherited))
    bm.timing_points.sort(key=lambda tp: (tp.time, not tp.uninherited))

    for line in sections.get("HitObjects", []):
        p = line.split(",")
        if len(p) < 4:
            continue
        try:
            x, y, t, typ = float(p[0]), float(p[1]), float(p[2]), int(p[3])
        except ValueError:
            continue
        new_combo = bool(typ & 4)
        if typ & _T_SPINNER:
            end = float(p[5]) if len(p) > 5 else t
            bm.hit_objects.append(HitObject(t, end, "spinner", x, y, new_combo))
        elif typ & _T_SLIDER and len(p) >= 8:
            try:
                slides = int(p[6])
                length = float(p[7])
            except ValueError:
                slides, length = 1, 0.0
            beat, sv = bm.beat_length_at(t)
            denom = bm.slider_multiplier * 100.0 * sv
            dur = (length / denom) * beat * slides if denom > 0 else 0.0
            bm.hit_objects.append(HitObject(t, t + dur, "slider", x, y, new_combo))
        else:
            bm.hit_objects.append(HitObject(t, t, "circle", x, y, new_combo))

    bm.hit_objects.sort(key=lambda o: o.time)
    return bm

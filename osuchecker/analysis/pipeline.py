"""One call: replay file in, everything the app can show out."""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from pathlib import Path

from ..config import Config
from ..replay.align import Alignment, align
from ..replay.beatmap import Beatmap, parse_beatmap
from ..replay.index import BeatmapIndex
from ..replay.osr import ParsedReplay, parse_replay
from .aim import AimResult, analyse_aim
from .episodes import Episode, find_episodes
from .judge import JudgeResult, judge_replay
from .recommend import Finding, build_findings
from .streams import BpmBucket, Section, analyse_sections, bucket_by_bpm
from .tapping import TapStats, analyse_tapping
from .training import Exercise, build_plan


@dataclass
class Analysis:
    replay: ParsedReplay
    beatmap: Beatmap | None = None
    judge: JudgeResult | None = None
    sections: list[Section] = field(default_factory=list)
    buckets: list[BpmBucket] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    aim: AimResult | None = None
    tapping: TapStats | None = None
    episodes: list[Episode] = field(default_factory=list)
    plan: list[Exercise] = field(default_factory=list)
    alignment: Alignment = field(default_factory=Alignment)
    error_key: str | None = None


    @property
    def mean_error(self) -> float:
        e = self.judge.errors() if self.judge else []
        return statistics.mean(e) if e else 0.0

    @property
    def ur(self) -> float:
        e = self.judge.errors() if self.judge else []
        return statistics.pstdev(e) * 10 if len(e) > 1 else 0.0

    def hand(self, key: str) -> tuple[int, float, float]:
        e = self.judge.errors(key) if self.judge else []
        if not e:
            return 0, 0.0, 0.0
        return len(e), statistics.mean(e), (statistics.pstdev(e) * 10 if len(e) > 1 else 0.0)

    @property
    def error(self) -> str:
        from ..i18n import t
        return t(self.error_key) if self.error_key else ""

    @property
    def hand_gap(self) -> float:
        """How much later the left hand is than the right, in ms."""
        _, mL, _ = self.hand("left")
        _, mR, _ = self.hand("right")
        return mL - mR

    @property
    def title(self) -> str:
        if not self.beatmap:
            return self.replay.path.stem
        return f"{self.beatmap.artist} - {self.beatmap.title} [{self.beatmap.version}]"


def analyse(path: str | Path, index: BeatmapIndex,
            cfg: Config | None = None, device: dict | None = None) -> Analysis:
    rp = parse_replay(path)
    a = Analysis(replay=rp)

    map_path = index.lookup(rp.beatmap_hash)
    if map_path is None:
        a.error_key = "analysis.map_not_found"
        return a

    a.beatmap = parse_beatmap(map_path)
    a.alignment = align(rp, a.beatmap)
    rp.shift_times(a.alignment.shift)
    a.judge = judge_replay(a.beatmap, rp)
    a.sections = analyse_sections(a.beatmap, a.judge)
    a.buckets = bucket_by_bpm(a.sections)
    a.aim = analyse_aim(a.beatmap, rp, a.judge)
    a.tapping = analyse_tapping(rp, a.judge)
    a.episodes = find_episodes(a.beatmap, a.judge, a.sections, a.aim)
    a.findings = build_findings(a.beatmap, rp, a.judge, a.sections,
                                a.buckets, device=device)
    a.plan = build_plan(a.buckets, a.episodes, a.aim, a.hand_gap)
    return a

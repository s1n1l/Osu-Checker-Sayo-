"""Application settings."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from .paths import data_file

CONFIG_PATH = data_file("config.json")


@dataclass
class Config:
    stable_songs: str = "S:/osu/Songs"
    stable_replays: str = "S:/osu/Replays"
    lazer_dir: str = ""
    only_when_focused: bool = True
    trigger_um: int = 500
    release_um: int = 400
    analog_hz: float = 1500.0
    language: str = "en"
    train_bpm: float = 180.0
    train_seconds: float = 30.0

    @staticmethod
    def load(path: str | Path = CONFIG_PATH) -> "Config":
        p = Path(path)
        if p.exists():
            try:
                return Config(**{**asdict(Config()),
                                 **json.loads(p.read_text(encoding="utf-8"))})
            except (json.JSONDecodeError, OSError, TypeError):
                pass
        c = Config()
        home = Path.home() / "AppData" / "Roaming" / "osu"
        if home.is_dir():
            c.lazer_dir = str(home)
        return c

    def save(self, path: str | Path = CONFIG_PATH) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

"""Application settings."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path

from .device.keys import DEFAULT_CODES, labels, normalise
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
    train_pattern: str = "stream"
    key_codes: list[int] = field(default_factory=lambda: list(DEFAULT_CODES))

    @property
    def keys(self) -> list[int]:
        """Virtual key codes bound to the three device slots."""
        return normalise(self.key_codes)

    @property
    def key_labels(self) -> list[str]:
        return labels(self.key_codes)

    @staticmethod
    def load(path: str | Path = CONFIG_PATH) -> "Config":
        p = Path(path)
        if p.exists():
            try:
                c = Config(**{**asdict(Config()),
                              **json.loads(p.read_text(encoding="utf-8"))})
                c.key_codes = normalise(c.key_codes)
                return c
            except (json.JSONDecodeError, OSError, TypeError):
                pass
        c = Config()
        home = Path.home() / "AppData" / "Roaming" / "osu"
        if home.is_dir():
            c.lazer_dir = str(home)
        return c

    def save(self, path: str | Path = CONFIG_PATH) -> None:
        self.key_codes = normalise(self.key_codes)
        Path(path).write_text(json.dumps(asdict(self), indent=2),
                              encoding="utf-8")

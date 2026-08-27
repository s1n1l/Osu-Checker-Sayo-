"""Finds the .osu file of a replay by its MD5 hash.

Stable keeps beatmaps as ordinary files. Lazer uses a content addressed
store where names are SHA-256 and carry no extension, so candidates there
are picked by file signature and then hashed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from ..paths import data_file

SIGNATURE = b"osu file format v"


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


class BeatmapIndex:
    """MD5 to .osu path, cached between runs."""

    def __init__(self, cache_path: str | Path | None = None):
        self.cache_path = (Path(cache_path) if cache_path
                           else data_file("beatmap_index.json"))
        self.by_md5: dict[str, str] = {}
        self.scanned: dict[str, float] = {}
        self._load()

    def _load(self) -> None:
        if self.cache_path.exists():
            try:
                data = json.loads(self.cache_path.read_text(encoding="utf-8"))
                self.by_md5 = data.get("by_md5", {})
                self.scanned = data.get("scanned", {})
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        self.cache_path.write_text(
            json.dumps({"by_md5": self.by_md5, "scanned": self.scanned}),
            encoding="utf-8")

    def lookup(self, md5: str) -> Path | None:
        p = self.by_md5.get((md5 or "").lower())
        if p and Path(p).exists():
            return Path(p)
        return None

    def scan_stable_songs(self, songs_dir: str | Path, progress=None) -> int:
        songs_dir = Path(songs_dir)
        if not songs_dir.is_dir():
            return 0
        added = 0
        files = list(songs_dir.glob("*/*.osu"))
        for i, f in enumerate(files):
            if progress and i % 200 == 0:
                progress(i, len(files), str(f.parent.name))
            try:
                md5 = _md5(f)
            except OSError:
                continue
            if md5 not in self.by_md5:
                added += 1
            self.by_md5[md5] = str(f)
        self.scanned[str(songs_dir)] = os.path.getmtime(songs_dir)
        return added

    def scan_lazer_files(self, lazer_dir: str | Path, progress=None) -> int:
        root = Path(lazer_dir) / "files"
        if not root.is_dir():
            return 0
        added = 0
        files = [p for p in root.rglob("*") if p.is_file()]
        for i, f in enumerate(files):
            if progress and i % 500 == 0:
                progress(i, len(files), f.name[:12])
            try:
                if f.stat().st_size > 4_000_000:
                    continue
                with open(f, "rb") as fh:
                    if not fh.read(len(SIGNATURE)).startswith(SIGNATURE[:8]):
                        continue
                md5 = _md5(f)
            except OSError:
                continue
            if md5 not in self.by_md5:
                added += 1
            self.by_md5[md5] = str(f)
        self.scanned[str(root)] = os.path.getmtime(root)
        return added

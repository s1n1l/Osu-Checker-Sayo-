"""Resource and user data locations.

Under PyInstaller the app runs from a temporary directory and the working
directory can be anything, so resources are looked up next to the code and
user data goes to APPDATA.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "osu-checker"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def resource_path(*parts: str) -> Path:
    """A file shipped with the application."""
    if is_frozen():
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base = Path(__file__).resolve().parent.parent
    return base.joinpath(*parts)


def data_dir() -> Path:
    """Directory for settings, indexes and caches."""
    if is_frozen():
        root = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    else:
        root = Path(__file__).resolve().parent.parent / "data"
    root.mkdir(parents=True, exist_ok=True)
    return root


def data_file(name: str) -> Path:
    return data_dir() / name

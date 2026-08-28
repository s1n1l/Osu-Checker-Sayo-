"""Runtime translation lookup."""
from __future__ import annotations

from importlib import import_module

LANGUAGES = {"en": "English", "uk": "Українська", "zh": "中文"}
DEFAULT = "en"

_cache: dict[str, dict[str, str]] = {}
_current = DEFAULT


def _table(code: str) -> dict[str, str]:
    if code not in _cache:
        try:
            mod = import_module(f".translations.{code}", __package__)
            _cache[code] = mod.STRINGS
        except (ImportError, AttributeError):
            _cache[code] = {}
    return _cache[code]


def set_language(code: str) -> None:
    global _current
    _current = code if code in LANGUAGES else DEFAULT
    _table(_current)


def current_language() -> str:
    return _current


def t(key: str, /, **params) -> str:
    """Looks up a string and fills its placeholders.

    The lookup key is positional-only so that a translation is free to use
    a placeholder called `key` -- which the device key bindings do.
    """
    text = _table(_current).get(key)
    if text is None:
        text = _table(DEFAULT).get(key, key)
    if not params:
        return text
    try:
        return text.format(**params)
    except (KeyError, IndexError, ValueError):
        return text


def missing_keys(code: str) -> list[str]:
    base = set(_table(DEFAULT))
    return sorted(base - set(_table(code)))

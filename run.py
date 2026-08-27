"""Entry point.

    python run.py                              normal start
    osu-checker.exe --selftest [replay.osr]    build check

The selftest exists for the packaged build: some failures appear only
after PyInstaller, and a windowed build has no console to show them.
"""
from __future__ import annotations

import sys
import traceback


def _selftest(replay: str | None) -> int:
    lines: list[str] = []
    ok = True

    def check(name: str, fn):
        nonlocal ok
        try:
            lines.append(f"OK   {name}: {fn()}")
        except Exception as exc:
            ok = False
            lines.append(f"FAIL {name}: {type(exc).__name__}: {exc}")
            lines.append(traceback.format_exc())

    from osuchecker.paths import data_dir, is_frozen, resource_path

    lines.append(f"frozen={is_frozen()}  python={sys.version.split()[0]}")
    lines.append(f"assets={resource_path('assets')}")
    lines.append(f"data={data_dir()}")

    check("osrparse import", lambda: __import__("osrparse").__version__)
    check("icon present", lambda: (resource_path("assets") / "icon.ico").exists())
    check("hidapi", lambda: len(__import__("hid").enumerate(0x8089, 0x0009)))
    check("beatmap index", lambda: len(
        __import__("osuchecker.replay.index", fromlist=["BeatmapIndex"])
        .BeatmapIndex().by_md5))
    check("QtMultimedia", lambda: __import__(
        "PySide6.QtMultimedia", fromlist=["QSoundEffect"]).QSoundEffect.__name__)
    check("gui modules", lambda: [
        __import__(f"osuchecker.gui.{name}", fromlist=["x"]).__name__.split(".")[-1]
        for name in ("theme", "playback", "trainer", "main")])
    check("metronome clicks", lambda: [
        __import__("osuchecker.gui.trainer", fromlist=["click_file"])
        .click_file(accent) for accent in (False, True)][0][-10:])
    def translations():
        from osuchecker.i18n import LANGUAGES, set_language, t
        out = {}
        for code in LANGUAGES:
            set_language(code)
            sample = t("tab.analysis")
            if sample == "tab.analysis":
                raise RuntimeError(f"{code}: strings not bundled")
            out[code] = sample
        set_language("en")
        return out

    check("translations", translations)

    if replay:
        def parse():
            from osuchecker.analysis.pipeline import analyse
            from osuchecker.replay.index import BeatmapIndex
            a = analyse(replay, BeatmapIndex())
            if a.error:
                return f"parsed, but {a.error}"
            return (f"{a.title} | error {a.mean_error:+.1f} ms, "
                    f"UR {a.ur:.0f}, episodes {len(a.episodes)}")
        check("replay analysis", parse)

    report = "\n".join(lines)
    try:
        out = data_dir() / "selftest.txt"
        out.write_text(report, encoding="utf-8")
        lines.append(f"\nreport: {out}")
    except OSError:
        pass
    try:
        print("\n".join(lines))
    except Exception:
        pass
    return 0 if ok else 1


def main() -> int:
    if "--selftest" in sys.argv:
        i = sys.argv.index("--selftest")
        arg = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
        return _selftest(arg)
    from osuchecker.gui.main import run
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

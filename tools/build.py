"""Builds the standalone application.

onedir rather than onefile: onefile unpacks about 160 MB into a temporary
folder on every start, which costs roughly ten seconds.

Two flags are here for antivirus reasons rather than technical ones.
--noupx keeps the executable unpacked, because a compressed section is the
strongest generic malware signal a scanner has, and --version-file fills in
the version resource, because an empty one reads as machine generated. The
real fix is a code signing certificate; these only reduce the count. See
SECURITY.md.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = "osu-checker"


def main() -> int:
    icon = ROOT / "assets" / "icon.ico"
    if not icon.exists():
        print("assets/icon.ico is missing, run tools/make_icon.py first")
        return 1
    version_file = ROOT / "version_info.txt"
    if not version_file.exists():
        print("version_info.txt is missing")
        return 1

    for d in ("build", "dist"):
        shutil.rmtree(ROOT / d, ignore_errors=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--windowed", "--noupx",
        "--name", NAME,
        "--icon", str(icon),
        "--version-file", str(version_file),
        "--add-data", f"{ROOT / 'assets'};assets",
        "--collect-binaries", "hid",
        "--copy-metadata", "osrparse",
        "--collect-submodules", "osuchecker.translations",
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "PySide6.QtWebEngineCore",
        str(ROOT / "run.py"),
    ]
    print("$", " ".join(cmd))
    res = subprocess.run(cmd, cwd=ROOT)
    if res.returncode != 0:
        return res.returncode

    exe = ROOT / "dist" / NAME / f"{NAME}.exe"
    if not exe.exists():
        print("build finished but the exe is missing")
        return 1
    total = sum(f.stat().st_size for f in (ROOT / "dist" / NAME).rglob("*")
                if f.is_file())
    print(f"\ndone: {exe}")
    print(f"folder size: {total / 1024 / 1024:.0f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

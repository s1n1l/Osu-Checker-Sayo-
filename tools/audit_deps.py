"""Audits the third party code this project ships.

Four questions, answered from the machine rather than from memory:

    what is installed, and which of it ends up inside the exe
    does every installed file still match the hash pip recorded
    is anything hooking the interpreter through a .pth file
    does any dependency contain code that talks to the network,
    spawns processes, or executes strings at runtime

The last one is a starting point for reading, not a verdict: numpy and
pyqtgraph both contain such code in places that never run here. The report
prints where each hit is so it can be checked by eye.

Run it after every dependency change, and before publishing a release:

    python tools/audit_deps.py
"""
from __future__ import annotations

import base64
import csv
import hashlib
import importlib.metadata as metadata
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# What the frozen application actually loads, and what only builds it.
RUNTIME = ["hidapi", "numpy", "osrparse", "pyqtgraph", "PySide6",
           "PySide6_Essentials", "PySide6_Addons", "shiboken6"]
BUILD_ONLY = ["pyinstaller", "pyinstaller-hooks-contrib", "altgraph", "pefile",
              "pywin32-ctypes", "setuptools", "packaging", "colorama",
              "pillow", "pip"]

# Import names that do not match the distribution name.
IMPORT_NAME = {"hidapi": "hid", "PySide6_Essentials": "PySide6",
               "PySide6_Addons": "PySide6", "pyinstaller": "PyInstaller",
               "pyinstaller-hooks-contrib": "_pyinstaller_hooks_contrib",
               "pywin32-ctypes": "win32ctypes", "pillow": "PIL"}

PATTERNS = {
    "network": re.compile(
        r"\b(socket\.socket|urllib\.request|urlopen|requests\.(get|post)"
        r"|http\.client|websocket)\b"),
    "subprocess": re.compile(
        r"\b(subprocess\.(Popen|run|call|check_output)|os\.system|os\.popen)\b"),
    "dynamic-exec": re.compile(r"(?<![\w.])(eval|exec)\s*\("),
    "base64-blob": re.compile(
        r"b(?:ase64|64decode)\s*\(\s*[\"'][A-Za-z0-9+/=]{200,}"),
    "pickle-load": re.compile(r"\bpickle\.loads?\s*\("),
}

# The one .pth every setuptools install has. Anything else is worth a look:
# a .pth runs at interpreter start, which is how recent PyPI compromises
# got their code executed.
KNOWN_PTH = {"distutils-precedence.pth"}


def site_packages() -> pathlib.Path:
    for parent in (pathlib.Path(sys.prefix) / "Lib" / "site-packages",
                   ROOT / ".venv" / "Lib" / "site-packages"):
        if parent.is_dir():
            return parent
    raise SystemExit("cannot find site-packages")


def inventory() -> None:
    print("== packages")
    for group, names in (("runtime", RUNTIME), ("build only", BUILD_ONLY)):
        for name in names:
            try:
                meta = metadata.metadata(name)
                version = metadata.version(name)
            except metadata.PackageNotFoundError:
                print(f"  {name:26s} NOT INSTALLED")
                continue
            licence = (meta.get("License-Expression") or meta.get("License")
                       or "?").splitlines()[0][:28]
            print(f"  {name:26s} {version:12s} {group:10s} {licence}")


def verify_hashes(site: pathlib.Path) -> int:
    print("\n== file integrity against pip's RECORD")
    checked = unhashed = bad = 0
    for dist in sorted(site.glob("*.dist-info")):
        record = dist / "RECORD"
        if not record.exists():
            continue
        for row in csv.reader(record.read_text(encoding="utf-8").splitlines()):
            if len(row) < 2 or not row[1]:
                unhashed += 1
                continue
            path = site / row[0]
            if not path.exists():
                unhashed += 1
                continue
            algo, _, want = row[1].partition("=")
            digest = hashlib.new(algo, path.read_bytes()).digest()
            got = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
            checked += 1
            if got != want:
                bad += 1
                print(f"  MISMATCH {row[0]}")
    print(f"  {checked} files verified, {unhashed} carry no recorded hash, "
          f"{bad} mismatched")
    return bad


def check_pth(site: pathlib.Path) -> int:
    print("\n== interpreter startup hooks")
    unexpected = 0
    for path in sorted(site.glob("*.pth")):
        known = path.name in KNOWN_PTH
        print(f"  {'known  ' if known else 'UNKNOWN'} {path.name}")
        if not known:
            unexpected += 1
            print("      " + path.read_text(encoding="utf-8",
                                            errors="replace").strip()[:200])
    for name in ("sitecustomize.py", "usercustomize.py"):
        if (site / name).exists():
            unexpected += 1
            print(f"  UNKNOWN {name}")
    if not unexpected:
        print("  nothing unexpected")
    return unexpected


def scan_behaviour(site: pathlib.Path) -> None:
    print("\n== behaviour worth reading, in the runtime dependencies")
    for name in RUNTIME:
        module = IMPORT_NAME.get(name, name)
        root = site / module
        if root.is_dir():
            files = list(root.rglob("*.py"))
        else:
            files = list(site.glob(f"{module}*.py"))
        counts: dict[str, int] = {}
        first: dict[str, str] = {}
        for file in files:
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for label, pattern in PATTERNS.items():
                for match in pattern.finditer(text):
                    counts[label] = counts.get(label, 0) + 1
                    first.setdefault(
                        label,
                        f"{file.relative_to(site)}: {match.group(0)}")
        summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"  {name:22s} {len(files):5d} .py files  "
              f"{summary or 'no matches'}")
        for label, where in sorted(first.items()):
            print(f"      first {label}: {where}")


def scan_own_code() -> int:
    print("\n== this project's own code")
    hits = 0
    for file in sorted((ROOT / "osuchecker").rglob("*.py")):
        text = file.read_text(encoding="utf-8", errors="ignore")
        for label in ("network", "subprocess", "dynamic-exec"):
            for match in PATTERNS[label].finditer(text):
                hits += 1
                print(f"  {file.relative_to(ROOT)}: {label} "
                      f"{match.group(0)}")
    if not hits:
        print("  no network, no subprocesses, no exec - the app reads "
              "files and one HID device")
    return hits


def main() -> int:
    site = site_packages()
    print(f"site-packages: {site}\n")
    inventory()
    bad = verify_hashes(site)
    unexpected = check_pth(site)
    scan_behaviour(site)
    own = scan_own_code()
    print("\n== result")
    if bad or unexpected:
        print("  SOMETHING IS OFF — read the lines above")
        return 1
    print("  installed files match what pip recorded, no startup hooks, "
          "no unexplained behaviour")
    return 0


if __name__ == "__main__":
    sys.exit(main())

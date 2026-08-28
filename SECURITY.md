# Security and antivirus

Two separate questions get mixed up whenever an antivirus flags a small
open-source tool, so they are answered separately here.

1. **Is there anything malicious in the code or its dependencies?**
   No. The audit below is reproducible: `python tools/audit_deps.py`.
2. **Why does VirusTotal show detections then?**
   Because of how the executable is packaged, not because of what it does.
   Details and what has been done about it are in the second half.

---

## What the app is allowed to do

The whole application does three things: it reads files from disk (`.osr`
replays, `.osu` beatmaps, its own settings), it talks to one USB HID device
(vendor `0x8089`, product `0x0009` — the SayoDevice O3C), and it draws a
window.

It has **no network code at all**. It never launches another process, never
executes generated code, and never writes to the device — only read requests
are sent over HID. `tools/audit_deps.py` checks this on every run by scanning
the project's own source:

```
== this project's own code
  no network, no subprocesses, no exec - the app reads files and one HID device
```

`Qt6Network.dll` is present in the build because Qt Multimedia links against
it. Nothing in this project calls it.

Key presses are captured through Windows Raw Input **filtered by device**:
only events carrying the O3C's `VID_8089&PID_0009` are ever looked at, and by
default only while the osu! window has focus. Nothing typed on the ordinary
keyboard reaches the app, and nothing is sent anywhere — recordings are saved
to a local `.json` file only when the Save button is pressed.

## Dependencies

Everything is installed from PyPI with pip, at pinned versions
(`requirements.txt`), and every one is a long-standing, widely used project.

### Shipped inside the executable

| Package | Version | Licence | Why it is here |
| --- | --- | --- | --- |
| [PySide6](https://pypi.org/project/PySide6/) (+ Essentials, Addons, shiboken6) | 6.11.2 | LGPL-3.0 / GPL | The Qt bindings the window is built with. Published by The Qt Company. |
| [numpy](https://pypi.org/project/numpy/) | 2.5.2 | BSD-3-Clause | All the arithmetic over replay frames. |
| [pyqtgraph](https://pypi.org/project/pyqtgraph/) | 0.14.0 | MIT | The plots. |
| [osrparse](https://pypi.org/project/osrparse/) | 7.0.1 | MIT | Reads the `.osr` replay format. |
| [hidapi](https://pypi.org/project/hidapi/) | 0.15.0 | BSD / GPL-3.0 | Cython bindings to hidapi, for reading analogue key travel. Published by the Trezor team. |

### Build-time only, not shipped

`pyinstaller`, `pyinstaller-hooks-contrib`, `altgraph`, `pefile`,
`pywin32-ctypes`, `setuptools`, `packaging`, `colorama`, `pillow`, `pip`.
None of these are part of the running application; `pillow` is used only by
`tools/make_icon.py`.

### What the audit checks

`tools/audit_deps.py` reports:

* **File integrity.** Every installed file is re-hashed and compared with the
  hash pip recorded at install time. Last run: **7708 files verified, 0
  mismatched.**
* **Interpreter startup hooks.** Recent PyPI compromises (LiteLLM and Telnyx
  in March 2026, Microsoft's `durabletask` in May 2026) ran their payload from
  a `.pth` file, which Python executes at startup. The only `.pth` present is
  setuptools' standard `distutils-precedence.pth`; there is no
  `sitecustomize.py` or `usercustomize.py`.
* **Behaviour worth reading.** Every runtime dependency is scanned for
  networking, subprocess spawning, `eval`/`exec`, long base64 blobs and
  `pickle.load`. The matches that exist are all in well-known places that
  never run here, and the report prints the file and line so they can be
  checked:
  * `numpy` — `urllib.request` inside `numpy/lib/_datasource.py` (the
    documented feature that lets `np.load` open a URL), `eval` in `f2py`,
    `subprocess` in the test suite, `pickle.load` in the `.npy` reader.
  * `pyqtgraph` — `eval` in its config-file parser, `subprocess` and
    `pickle` in its interactive debug console. None of those modules are
    imported by this app.
  * `PySide6` — `subprocess` in `pyside_tool.py`, the developer CLI
    (`pyside6-designer` and friends), not in the runtime libraries.
  * `hidapi`, `osrparse`, `shiboken6` — no matches at all.
* **No base64 blobs** anywhere in the runtime dependencies.

None of the packages used here appear in any known supply-chain incident.

---

## The VirusTotal detections

Every figure below belongs to a specific build. PyInstaller output is not
reproducible byte for byte, so **each release has its own hash and needs its
own scan** — the hash and a VirusTotal link are published in the release
notes, and the table here is the running record.

| Release | Detections | Notes |
| --- | --- | --- |
| v1.1.0 | 10 / 68 | `c0446a22…04c75`, scanned 2026-08-27. No version resource. |
| v1.2.0 | see the release notes | first build with a version resource and UPX explicitly off |

### Checking a release yourself

Do not take this document's word for it. Hash the file you downloaded and
look it up:

```
certutil -hashfile osu-checker.exe SHA256
```

Paste that hash into [virustotal.com](https://www.virustotal.com/) — if the
file has been scanned before you get the existing report without uploading
anything. Compare it with the hash in the release notes: if they differ, you
did not get the file that was published here.

### Why the v1.1.0 result is a false positive

The v1.1.0 binary scored 10 out of 68, and the shape of that result says
what it is:

* **Every verdict is generic or machine-learning, with no family name** —
  `Wacatac.B!ml`, `Win64:Malware-gen`, `TR/W64.Malware`, `Unsafe`,
  `Malicious (score: 99)`, `Dropper.Agent`. None of them identify actual
  malware; they identify "this looks unusual".
* **It is about seven distinct engines, not ten.** Avast and AVG share an
  engine, as do Avira and WithSecure.
* **Every high-reputation engine is clean**: Kaspersky, ESET, BitDefender,
  Sophos, Symantec, Trend Micro, Malwarebytes, Fortinet, CrowdStrike, Google.
* **The sandbox verdict is clean.** VirusTotal's Zenbox detonated the binary
  and reported no malicious behaviour, at 99% confidence.

### Why it triggers them

* PyInstaller appends the entire Python application to the executable as a
  compressed overlay. On this build that is ~5.6 MB at entropy 7.9994 out of
  8.0 — statistically indistinguishable from encrypted or packed payload,
  which is exactly what generic heuristics look for.
* The PyInstaller bootloader imports `CreateToolhelp32Snapshot`,
  `Process32First/Next`, `OpenProcessToken` and `VirtualProtect`. That
  combination — enumerate processes, open a token, make memory executable —
  is the classic injector fingerprint, even though here it only unpacks and
  starts Python.
* The file has **no code signature** and, before v1.2.0, **no version
  information at all**. An unsigned binary with an empty version resource and
  zero download reputation is precisely the profile these heuristics were
  trained on.

UPX is *not* involved — it was never applied, and it is now explicitly
disabled in the build.

### What has been done about it

* A version resource (`version_info.txt`) is now compiled into the
  executable: company, product, description, version and copyright.
* UPX is explicitly off (`--noupx`, and `upx=False` in the spec file), so no
  section is packed.
* This document exists, and the READMEs point at it.
* Ready-to-send false-positive reports, with the verified submission forms
  for each engine, are in
  [docs/false-positive-reports.md](docs/false-positive-reports.md). They have
  to be sent per release: the hash changes every build, and an unsigned file
  carries no reputation from one version to the next.

Expect these to reduce the number, not to zero it. **The only real fix is a
code signing certificate** (roughly 200–400 USD/year for OV; EV additionally
buys instant SmartScreen trust), which is not currently in place. Until then
this is the honest position: a small, unsigned, PyInstaller-packed tool from
an account with no download history is exactly what generic heuristics are
built to flag, and no amount of explaining changes what the scanner does.
What can be offered instead is the source, a reproducible dependency audit,
a sandbox verdict, and the ability to build the thing yourself.

### If you would rather not trust the binary

Build it yourself. The binary will not be byte-for-byte identical to the
released one -- PyInstaller stamps timestamps into it -- but it is the same
application from the same source:

```
git clone https://github.com/s1n1l/Osu-Checker-Sayo-
cd Osu-Checker-Sayo-
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python tools/audit_deps.py     # verify the dependencies
.venv\Scripts\python tools/build.py          # or just run: python run.py
```

Running from source needs no build step at all: `python run.py`.

## Reporting a problem

If you find something genuinely wrong — a security issue in the code, or a
dependency that turns out to be compromised — open an issue on the GitHub
repository.

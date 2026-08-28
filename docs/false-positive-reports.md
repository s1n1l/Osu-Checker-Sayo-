# False-positive reports

Ready-to-send drafts for the engines that flagged the packaged build. Fill in
the release URL and the SHA-256 of the file you are actually submitting, then
attach the `.exe` (zip it if the form asks for an archive; use `infected` as
the password only if the form requires one).

Submit **after** publishing a build, so the hash you report is the hash people
download. Detections usually clear within a few days to two weeks, and they
come back on the next release — the hash changes every build, and the file has
no signature to carry reputation across versions.

Background and evidence: [SECURITY.md](../SECURITY.md).

## Where to send it

Links checked against AV-Comparatives' vendor list, August 2026.

| Engine | Form |
| --- | --- |
| **Microsoft** (Defender — highest impact by far) | https://www.microsoft.com/en-us/wdsi/filesubmission?persona=HomeUser |
| **Avast** (also clears AVG — same engine) | https://www.avast.com/false-positive-file-form.php |
| **AVG** | https://www.avg.com/en-us/false-positive-file-form |
| **Avira** (also clears WithSecure — same engine) | https://www.avira.com/en/analysis/submit |
| **WithSecure** | https://www.withsecure.com/en/support/contact-support/submit-a-sample |
| **K7** | https://support.k7computing.com/index.php?/ticket/submit-ticket |

Cylance / Arctic Wolf, Cynet, SecureAge and Zillya have no public
false-positive form. Reach them through the support address on their own site,
or through the VirusTotal report page for the file — several vendors monitor
comments there.

## What to send

Choose "false positive" / "incorrectly detected file" where the form asks, and
say the detection is heuristic. Paste this into the description box:

---

**Subject:** False positive on osu-checker.exe (PyInstaller build, open source)

This file is the release build of osu-checker, an open-source osu! gameplay
analyser for the SayoDevice O3C keypad. It is detected as
`<detection name your product reports>`, which I believe is a false positive
on PyInstaller packaging.

* File: `osu-checker.exe`
* SHA-256: `<hash>`
* Version: `<version>`
* Download: `<release URL>`
* Source: https://github.com/s1n1l/Osu-Checker-Sayo-
* Licence: MIT

What the program does: it reads osu! replay (`.osr`) and beatmap (`.osu`)
files from disk, reads analogue key travel from one USB HID device
(VID 0x8089, PID 0x0009) using read-only requests, and draws a Qt window.
It contains no networking code of any kind, starts no other processes, and
executes no generated code. The full source is in the repository above and
can be rebuilt from it.

Why I think the detection is heuristic: the application is packaged with
PyInstaller 6.22.2, which appends the Python runtime and bytecode to the
executable as a high-entropy compressed overlay, and whose bootloader imports
`CreateToolhelp32Snapshot`, `Process32First/Next`, `OpenProcessToken` and
`VirtualProtect`. That combination is what generic and ML detections are
matching. UPX is not used. The build is not code-signed, which is being
worked on.

Supporting evidence: on VirusTotal the file is clean in Kaspersky, ESET,
BitDefender, Sophos, Symantec, Trend Micro, Malwarebytes, Fortinet,
CrowdStrike and Google, and the Zenbox sandbox verdict is clean at 99%
confidence. Every detection is generic or ML with no malware family attached.

Please re-examine the file. Happy to provide anything else useful.

---

## Release checklist

So the transparency claims in [SECURITY.md](../SECURITY.md) stay true, every
release needs these four things:

1. `python tools/audit_deps.py` — must end with "installed files match what
   pip recorded".
2. `osu-checker.exe --selftest <replay.osr>` against the frozen build, not
   the source tree. Several bugs only appear after PyInstaller.
3. `certutil -hashfile osu-checker.exe SHA256`, and put that hash **in the
   release notes** together with the VirusTotal permalink for it. Readers
   are told to check the hash they downloaded against it.
4. Add the result to the table in SECURITY.md, then send the reports below.

## After submitting

Note the date and the ticket number here, so the next release does not repeat
work:

| Date | Engine | Ticket / reference | Outcome |
| --- | --- | --- | --- |
| | | | |

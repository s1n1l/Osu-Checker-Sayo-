# False-positive reports

Ready-to-send drafts for the engines that flagged the packaged build. The
text below is filled in for v1.2.0; for a later release swap the version, the
hash, the download URL and the VirusTotal link. Attach the `.exe` (zip it if
the form asks for an archive; use `infected` as the password only if the form
requires one).

Submit **after** publishing a build, so the hash you report is the hash people
download. Detections usually clear within a few days to two weeks, and they
come back on the next release — the hash changes every build, and the file has
no signature to carry reputation across versions.

Background and evidence: [SECURITY.md](../SECURITY.md).

## Who to send it to, for v1.2.0

Eight detections from six distinct engines. Send in this order — the first
one matters more than the rest put together, because Defender ships on every
Windows machine.

| Priority | Engine | Its verdict on v1.2.0 | Form |
| --- | --- | --- | --- |
| 1 | **Microsoft** | `Trojan:Win32/Wacatac.B!ml` | https://www.microsoft.com/en-us/wdsi/filesubmission?persona=HomeUser |
| 2 | **Avast** (clears AVG too — same engine) | `Win64:Malware-gen` | https://www.avast.com/false-positive-file-form.php |
| 2 | **AVG** (submit only if Avast does not clear it) | `Win64:Malware-gen` | https://www.avg.com/en-us/false-positive-file-form |
| 3 | **Avira** (clears F-Secure too — same engine) | `TR/W64.Malware` | https://www.avira.com/en/analysis/submit |
| 3 | **F-Secure** (only if Avira does not clear it) | `Trojan.TR/W64.Malware` | https://www.withsecure.com/en/support/contact-support/submit-a-sample |
| 4 | **K7** | `Trojan ( 006e4d5e1 )` | https://support.k7computing.com/index.php?/ticket/submit-ticket |
| 5 | **Cynet** | `Malicious (score: 99)` | no public form — support address on cynet.com, or comment on the VirusTotal report |
| 5 | **APEX** | `Malicious` | no public form — same approach |

Cylance and Zillya flagged v1.1.0 and pass v1.2.0, so they need nothing.

Links checked against AV-Comparatives' vendor list, August 2026.

## What to send

Choose "false positive" / "incorrectly detected file" where the form asks, and
say the detection is heuristic. Paste this into the description box:

---

**Subject:** False positive on osu-checker.exe v1.2.0 (PyInstaller build, open source)

This file is the release build of osu-checker, an open-source osu! gameplay
analyser for the SayoDevice O3C keypad. Your product detects it as
`<paste the verdict from the table above>`, which I believe is a false positive
on PyInstaller packaging.

* File: `osu-checker.exe`
* SHA-256: `3d78f27c01bbef5212aa5f3616b973657ca8be0a214cb1e34f6ef35e4dffb6e2`
* Version: 1.2.0
* Download: https://github.com/s1n1l/Osu-Checker-Sayo-/releases/tag/v1.2.0
* Source: https://github.com/s1n1l/Osu-Checker-Sayo-
* Licence: MIT
* VirusTotal: https://www.virustotal.com/gui/file/3d78f27c01bbef5212aa5f3616b973657ca8be0a214cb1e34f6ef35e4dffb6e2/detection

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

Supporting evidence: 8 of 71 engines flag it, from 6 distinct engines, and
not one of the eight names a malware family — they are generic buckets
(`Win64:Malware-gen`, `TR/W64.Malware`), a machine-learning guess
(`Wacatac.B!ml`), a bare score, or a signature id. The file is clean in
Kaspersky, ESET, BitDefender, Sophos, Symantec, Trend Micro, McAfee,
Malwarebytes, Fortinet, CrowdStrike, SentinelOne and Google, and the Zenbox
sandbox classified it harmless at 99% confidence. The only crowdsourced YARA
rule that matches is "PyInstaller", whose own description states that it does
not by itself mean the file is malicious.

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

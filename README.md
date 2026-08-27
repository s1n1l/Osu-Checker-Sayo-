# osu-checker

<img src="assets/logo.png" width="96" align="right">

Gameplay analyser for osu! built around the **SayoDevice O3C** with Gateron
KS-20 magnetic switches. It compares what your fingers and hand actually did
with what the game registered, and sorts the mistakes into technique, device
settings and game settings.

Languages: **English · [Українська](README.uk.md) · [中文](README.zh.md)**

---

## Download

Grab the latest `osu-checker-windows.zip` from
[Releases](../../releases), unpack it anywhere and run `osu-checker.exe`.
Windows only. Python is not required.

## Tabs

### Analysis

Drop an `.osr` on the window, or press *Latest osu! replay*. Both osu!stable
and exported osu!lazer replays work.

**Overview** — hit error and UR per hand, a histogram with the 300/100 window
markers, error across the map, and a per-BPM table. The key column is
**drift**: how much the error grew from the start of a stream to its end.

**Aim** — where the cursor landed relative to the circle centre. Three
different effects are kept apart:

| Metric | What it means |
|---|---|
| offset | the cursor consistently lands off to one side |
| spread | it lands around the centre but far from it |
| overshoot | it flies past the target and comes back |

Plus a breakdown by jump distance and by direction across eight sectors.

**Problem spots** — the most expensive stretches of the map with the time,
what was lost and the cause: *fell behind*, *rushed*, *scatter*, *aim*.

### Recording

Three sources at once:

| Source | What it gives | Rate |
|---|---|---|
| Raw Input | key presses from the O3C only | event driven, ~1 ms |
| HID polling | travel of all three keys, in µm | ~2660 Hz (0.37 ms) |
| GetCursorPos | cursor position | polled at 500 Hz |

This exists because an osu! replay writes only about 62 frames per second,
rounding every timing to ~16 ms. After you stop, the tab shows the real press
depth per key and the margin left to the actuation point.

A saved recording can be attached on the Analysis tab, which adds press depth
to the findings — something a replay cannot contain at all.

### Training

The plan is built from the numbers of the last analysis. Every exercise has a
**measurable criterion** this same app checks on your next replay. *Find maps*
searches your own collection for maps with streams at the target BPM.

### Settings

Language, osu! paths, and the beatmap index (MD5 → `.osu`).

## How the causes are told apart

| What the data shows | Conclusion |
|---|---|
| Error grows from the start of a stream to its end | Not enough speed, the hand loses the tempo |
| More presses than notes, error otherwise flat | Overstreaming |
| Left and right hand have different mean error | Hands out of sync, technique |
| A flat offset across many replays | Audio offset or latency |
| A repeat press faster than 45 ms | Double actuation, Rapid Trigger |
| Cursor far from the centres on that stretch | Aim fell apart, not tapping |
| Press depth barely clears the threshold | Under-pressing, lower the actuation point |

## The device

SayoDevice O3C, `VID 0x8089 / PID 0x0009`. The app **only reads**: it sends
status read requests and never touches the configuration.

The protocol is **request/response**, not a stream. The device stays silent
until asked; the web configurator polls it about 20 times a second, which is
why it looks like a stream from the outside.

The ceiling depends on the USB polling rate set on the device itself. At
**8000 Hz** one round trip takes **0.37 ms**, roughly three USB frames, so all
three keys can be sampled about 2660 times a second. At 1000 Hz a round trip
would take about 2 ms.

Request, usage page `0xFF12`, 1024 byte packet:

```
0x00  report_id 0x22
0x01  echo 0x03
0x02  checksum u16 LE   (the packet summed as u16 with the slot zeroed)
0x04  len u16 LE = 0x0004
0x06  id 0x15
0x07  index 0x01        <- index 1 is the one that returns millimetres
```

The reply is `len=0x000a` followed by three `u16` values: key travel in
micrometres, `0` at rest and `4000` at the full 4 mm travel. Index 0 returns
the raw ADC of one key, index 2 the raw ADC of all three. Key indexes are
`P = 0, V = 1, B = 2`.

Interface `0xFF11` speaks the same protocol in 64 byte packets; request `0x1F`
returns 16 consecutive samples of a single key, but the key cannot be
selected, so `0xFF12` is used instead.

The polling rate can be capped in the Recording tab, though there is little
point: free running costs about 9% of one core, and that is cheaper than any
accurate cap, because waiting out a quantum on Windows eats more than it saves.

### Limitations

- The 50 and miss counts differ slightly from osu!, because the game judges
  slider heads separately. The 300 count matches to within about 0.1%, and the
  tapping analysis is built on that.
- Attaching a recording to a replay is manual: press depth is taken as an
  aggregate over the session rather than aligned to individual notes.
- Playfield geometry for the cursor is computed with the osu!stable formula
  (512×384 inside a 640×480 virtual screen, shifted 8 virtual pixels down) and
  is read from the osu! window while it has focus.

## About key auto-repeat

Holding a key makes Windows send `WM_KEYDOWN` every ~30 ms after a ~500 ms
delay, and Raw Input reports those too. The recorder discards them by key
state — otherwise a two second hold would look like 50 presses.

## Privacy

The recorder uses Raw Input, which reports the HID device handle. Only events
from `VID_8089&PID_0009` are recorded, and by default only while the osu!
window has focus. Anything typed on a regular keyboard is not visible to the
app.

## Building from source

Windows, Python 3.12+.

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py
```

To produce the distributable folder:

```
.venv\Scripts\python.exe -m pip install pyinstaller pillow
.venv\Scripts\python.exe tools\make_icon.py
.venv\Scripts\python.exe tools\build.py
```

The result is `dist\osu-checker\` — zip that folder and it runs on any Windows
machine without Python. The build is `onedir` on purpose: `onefile` unpacks
about 160 MB into a temporary folder on every start.

## Diagnostics

The packaged app has a self-test that runs without a window and writes a
report to `%APPDATA%\osu-checker\selftest.txt`:

```
osu-checker.exe --selftest
osu-checker.exe --selftest "path\to\replay.osr"
```

It checks the `osrparse` import, the icon, HID visibility of the device, the
size of the beatmap index and, given a path, a full replay analysis. This
matters for the packaged build specifically: some failures appear only after
PyInstaller and a windowed build has no console to show them.

## Application data

In development, the `data/` folder. In the packaged app,
`%APPDATA%\osu-checker`: `config.json`, the beatmap index
`beatmap_index.json` and the profile cache `map_profiles.json`.

## Adding a language

Copy `osuchecker/translations/en.py`, translate the values, keep the keys and
the `{placeholders}` unchanged, then add the language code to `LANGUAGES` in
`osuchecker/i18n.py`.

## Credits

The O3C HID protocol was worked out from the device itself, with the packet
framing based on public reverse engineering notes by
[khang06](https://gist.github.com/khang06/6186543b560548370ce7cc08cad7f710)
and the clean room firmware project
[ankurCES/sayofw-o3c](https://github.com/ankurCES/sayofw-o3c).

Replay parsing uses [osrparse](https://github.com/kszlim/osu-replay-parser).

Not affiliated with osu! or SayoDevice.

## License

MIT, see [LICENSE](LICENSE).

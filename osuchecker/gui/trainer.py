"""In-app tapping trainer: play a rhythm and see where it comes apart.

The exercise is a pattern -- bursts, doubles, triples, a long stream --
built from runs of notes separated by rests, and presses are judged
against those note times the way the game judges a map. Holding one
endless tempo is still there as the "stream" pattern, but it only trains
stamina; what usually costs points is entering a burst after a rest, and
that only shows up when there are rests to enter after.

Taps are read from the O3C through Raw Input, so what is measured is the
same signal the game receives. See analysis.patterns for the rhythm and
the judging, which are plain arithmetic and tested on their own.
"""
from __future__ import annotations

import math
import statistics
import struct
import threading
import time
import wave

import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (QCheckBox, QComboBox, QGridLayout, QHBoxLayout,
                               QLabel, QPushButton, QSpinBox, QVBoxLayout,
                               QWidget)

from ..analysis import patterns as pat
from ..config import Config
from ..device.keys import key_name
from ..device.rawinput import RawKeyboardListener
from ..i18n import t
from ..paths import data_file
from . import theme
from .lane import NoteLane
from .widgets import Card, StatTile, dim_label, muted_label

TAPS_PER_BEAT = 4
COUNT_IN_BEATS = 4
ROLL_TAPS = 16
SAMPLE_RATE = 44100

# Two presses this close together are not a human alternating hands: 20 ms
# apart is a 750 BPM stream. They come from a switch bouncing, or from the
# input thread being starved and timestamping two queued presses at once.
# Left in the mean they are ruinous -- a single 0.1 ms gap reads as 150000
# BPM -- so they are counted separately and reported instead.
MIN_GAP_MS = 20.0
TICK_MS = 10
# A redraw costs 12 to 15 ms of blocked event loop, and a metronome click
# that collides with one comes out late. Two and a half redraws a second is
# plenty for a plot nobody stares at mid-exercise.
PLOT_MS = 400
PLOT_POINTS = 400
# The lane only scrolls; judging runs slower and catches up to it.
FRAME_MS = 16
JUDGE_MS = 50
# How far off a note a press may be and still count as that note. Half a
# gap, so a press can never be closer to its neighbour than to its own
# note, and never wider than the 100 ms the game itself allows for a 50.
def hit_window(bpm: float) -> float:
    return min(100.0, pat.tap_interval(bpm) * 0.5)


def click_file(accent: bool) -> str:
    path = data_file("click_accent.wav" if accent else "click.wav")
    if path.exists():
        return str(path)
    freq = 1600.0 if accent else 1050.0
    length = int(SAMPLE_RATE * 0.028)
    frames = bytearray()
    for i in range(length):
        envelope = math.exp(-i / (SAMPLE_RATE * 0.006))
        value = int(26000 * envelope * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
        frames += struct.pack("<h", value)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(bytes(frames))
    return str(path)


class TrainerTab(QWidget):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.listener: RawKeyboardListener | None = None
        self.keys: dict[int, str] = {}
        self.down: set[str] = set()
        self.taps: list[tuple[float, str]] = []
        self.notes: list[float] = []
        self.openers: set[int] = set()
        self.result = pat.PatternResult()
        # Presses arrive on the Raw Input thread and are read on the GUI
        # thread.
        self.lock = threading.Lock()
        self.last_plot = 0.0
        # Filled in on stop, from the listener: how often the input thread
        # was scheduled too late to time a press properly.
        self.stalls = (0, 0)
        self.running = False
        self.start_time = 0.0
        self.grid_start = 0.0
        self.next_beat = 0.0
        self.beat_index = 0

        self.click = QSoundEffect(self)
        self.click.setSource(QUrl.fromLocalFile(click_file(False)))
        self.click.setVolume(0.35)
        self.accent = QSoundEffect(self)
        self.accent.setSource(QUrl.fromLocalFile(click_file(True)))
        self.accent.setVolume(0.45)

        root = QVBoxLayout(self)
        root.setSpacing(12)

        head = QLabel(t("tab.trainer"))
        head.setObjectName("h1")
        root.addWidget(head)
        root.addWidget(dim_label(t("trn.info")))
        self.keys_hint = muted_label("")
        root.addWidget(self.keys_hint)

        controls = Card(t("trn.controls_title"))
        row = QHBoxLayout()
        row.addWidget(QLabel(t("trn.pattern")))
        self.pattern = QComboBox()
        self.pattern.setMinimumWidth(190)
        for preset in pat.PATTERNS:
            self.pattern.addItem(t(preset.name_key), preset.key)
        chosen = self.pattern.findData(cfg.train_pattern)
        self.pattern.setCurrentIndex(max(0, chosen))
        self.pattern.currentIndexChanged.connect(self._pattern_changed)
        row.addWidget(self.pattern)
        row.addSpacing(16)
        row.addWidget(QLabel(t("trn.target_bpm")))
        self.bpm = QSpinBox()
        self.bpm.setRange(60, 400)
        self.bpm.setSingleStep(5)
        self.bpm.setValue(int(cfg.train_bpm))
        self.bpm.valueChanged.connect(self._retarget)
        row.addWidget(self.bpm)
        row.addSpacing(16)
        row.addWidget(QLabel(t("trn.duration")))
        self.seconds = QSpinBox()
        self.seconds.setRange(5, 300)
        self.seconds.setSingleStep(5)
        self.seconds.setValue(int(cfg.train_seconds))
        row.addWidget(self.seconds)
        row.addSpacing(16)
        self.sound = QCheckBox(t("trn.sound"))
        self.sound.setChecked(True)
        row.addWidget(self.sound)
        row.addStretch(1)
        self.btn = QPushButton(t("trn.start"))
        self.btn.setObjectName("primary")
        self.btn.clicked.connect(self.toggle)
        row.addWidget(self.btn)
        host = QWidget()
        host.setLayout(row)
        controls.add(host)
        self.pattern_hint = muted_label("")
        controls.add(self.pattern_hint)
        root.addWidget(controls)

        self.lane = NoteLane()
        self.lane.set_idle_text(t("trn.lane_idle"))
        root.addWidget(self.lane)
        root.addWidget(muted_label(t("trn.lane_hint")))

        grid = QGridLayout()
        grid.setSpacing(10)
        self.cards: dict[str, StatTile] = {}
        for column, (key, caption, hint) in enumerate((
                ("bpm", t("trn.card_bpm"), t("trn.card_bpm_hint")),
                ("error", t("trn.card_error"), t("trn.card_error_hint")),
                ("ur", t("trn.card_ur"), t("trn.card_ur_hint")),
                ("hits", t("trn.card_hits"), t("trn.card_hits_hint")),
                ("left", t("trn.card_left"), t("trn.card_left_hint")),
        )):
            tile = StatTile(caption, "—", hint)
            if key == "bpm":
                tile.value.setObjectName("huge")
            grid.addWidget(tile, 0, column)
            grid.setColumnStretch(column, 1)
            self.cards[key] = tile
        root.addLayout(grid)

        self.beat = QLabel("")
        self.beat.setObjectName("h2")
        self.beat.setAlignment(Qt.AlignCenter)
        self.beat.setMinimumHeight(34)
        root.addWidget(self.beat)

        self.plot = pg.PlotWidget()
        theme.style_plot(self.plot, title=t("trn.plot_title"))
        self.plot.setLabel("left", t("trn.plot_y"), **theme.plot_label_style())
        self.plot.setLabel("bottom", t("trn.plot_x"), **theme.plot_label_style())
        self.plot.setMinimumHeight(190)
        # One dot per press, not a joined line: the intervals are discrete
        # samples, and a line between them draws full-height strokes across
        # the plot whenever one press is late, which reads as the graph
        # flying off the top.
        self.curve = self.plot.plot(pen=None, symbol="o", symbolSize=4,
                                    symbolPen=None,
                                    symbolBrush=theme.ACCENT)
        self.target_line = pg.InfiniteLine(
            pos=0, angle=0, pen=pg.mkPen(theme.GOOD, width=2))
        self.plot.addItem(self.target_line)
        root.addWidget(self.plot, 1)

        root.addWidget(muted_label(t("trn.plot_hint")))

        self.summary = QLabel(t("trn.idle"))
        self.summary.setWordWrap(True)
        root.addWidget(self.summary)
        self.refresh_keys()
        self._retarget()

        # 10 ms, not 2: audio latency dwarfs the difference, and a 2 ms
        # timer floods the event loop badly enough to starve the thread the
        # presses are timed on.
        self.ticker = QTimer(self)
        self.ticker.setTimerType(Qt.PreciseTimer)
        self.ticker.setInterval(TICK_MS)
        self.ticker.timeout.connect(self._tick)

        self.ui_timer = QTimer(self)
        self.ui_timer.setInterval(JUDGE_MS)
        self.ui_timer.timeout.connect(self._refresh)

        self.frame_timer = QTimer(self)
        self.frame_timer.setInterval(FRAME_MS)
        self.frame_timer.timeout.connect(self._scroll)

    def refresh_keys(self) -> None:
        """Picks up the key binding from settings without a restart."""
        self.keys = {code: key_name(code) for code in self.cfg.keys}
        self.keys_hint.setText(
            t("trn.keys_hint", keys=" · ".join(self.cfg.key_labels)))

    def _pattern_changed(self) -> None:
        self.cfg.train_pattern = self.pattern.currentData()
        self._retarget()

    @property
    def preset(self):
        return pat.BY_KEY.get(self.pattern.currentData(), pat.PATTERNS[0])

    def _retarget(self) -> None:
        interval = self.tap_interval
        self.target_line.setValue(interval)
        self.plot.setYRange(interval * 0.5, interval * 1.5)
        self.pattern_hint.setText(t(self.preset.hint_key))
        if not self.running:
            self.cards["bpm"].set_value(f"{self.bpm.value()}")
            self.cards["error"].set_value("—")
            self.cards["ur"].set_value("—")
            self.cards["hits"].set_value("—")
            self.cards["left"].set_value(f"{self.seconds.value()}")

    @property
    def tap_interval(self) -> float:
        return 15000.0 / self.bpm.value()

    @property
    def beat_interval(self) -> float:
        return 60000.0 / self.bpm.value()

    def toggle(self) -> None:
        self.stop() if self.running else self.start()

    def start(self) -> None:
        self.cfg.train_bpm = float(self.bpm.value())
        self.cfg.train_seconds = float(self.seconds.value())
        self.cfg.train_pattern = self.pattern.currentData()
        self.cfg.save()

        self.refresh_keys()
        self.stalls = (0, 0)
        self.listener = RawKeyboardListener(on_key=self._on_key)
        if not self.listener.start():
            self.summary.setText(t("trn.no_device",
                                   message=self.listener.error or ""))
            return
        with self.lock:
            self.taps.clear()
            self.down.clear()
        self.last_plot = 0.0
        self.running = True
        self.beat_index = -COUNT_IN_BEATS
        self.start_time = time.perf_counter() * 1000.0
        self.next_beat = self.start_time
        self.grid_start = self.start_time + COUNT_IN_BEATS * self.beat_interval
        self.notes, self.openers = pat.build(
            self.preset, float(self.bpm.value()), float(self.seconds.value()),
            start=self.grid_start)
        self.result = pat.PatternResult(notes=len(self.notes))
        self.lane.set_rhythm(self.notes, self.openers, self.beat_interval,
                             hit_window(self.bpm.value()))
        self.btn.setText(t("trn.stop"))
        self.summary.setText(t("trn.count_in"))
        self._retarget()
        self.ticker.start()
        self.ui_timer.start()
        self.frame_timer.start()

    def stop(self) -> None:
        self.running = False
        self.ticker.stop()
        self.ui_timer.stop()
        self.frame_timer.stop()
        if self.listener:
            self.stalls = (getattr(self.listener, "stalled", 0),
                           getattr(self.listener, "max_stall_ms", 0))
            self.listener.stop()
            self.listener = None
        self.btn.setText(t("trn.start"))
        self.beat.setText("")
        self.lane.set_judged(self.result.matched, self._press_marks(), False)
        self._summarise()

    def _on_key(self, stroke) -> None:
        """Runs on the Raw Input thread, so it does as little as possible."""
        name = self.keys.get(stroke.vkey)
        if name is None or not self.running:
            return
        with self.lock:
            if not stroke.down:
                self.down.discard(name)
                return
            if name in self.down:
                return
            self.down.add(name)
            now = stroke.t * 1000.0
            if now >= self.grid_start:
                self.taps.append((now, name))

    def _snapshot(self) -> list[tuple[float, str]]:
        with self.lock:
            return list(self.taps)

    def _press_marks(self) -> list[tuple[float, str]]:
        """Presses as the lane wants them, newest tail only."""
        return self._snapshot()[-120:]

    def _scroll(self) -> None:
        self.lane.set_now(time.perf_counter() * 1000.0)

    def _tick(self) -> None:
        now = time.perf_counter() * 1000.0
        if now >= self.next_beat:
            # Beats missed while the machine was busy are skipped, not
            # replayed: catching up one click per tick turns a hiccup into a
            # burst of clicks, which makes the stall worse.
            missed = int((now - self.next_beat) // self.beat_interval)
            late = now - self.next_beat
            self.beat_index += missed + 1
            self.next_beat += (missed + 1) * self.beat_interval
            if self.sound.isChecked() and late < self.beat_interval * 0.5:
                effect = (self.accent if (self.beat_index - 1) % 4 == 0
                          else self.click)
                effect.play()
        if now - self.grid_start >= self.seconds.value() * 1000.0:
            self.stop()

    def _rolling(self, taps) -> tuple[float, float, float]:
        if len(taps) < 4:
            return 0.0, 0.0, 0.0
        times = [x[0] for x in taps]
        window = times[-ROLL_TAPS:]
        gaps = [window[i] - window[i - 1] for i in range(1, len(window))]
        gaps = [g for g in gaps if MIN_GAP_MS <= g < self.tap_interval * 4]
        if not gaps:
            return 0.0, 0.0, 0.0
        mean_gap = statistics.mean(gaps)
        bpm = 15000.0 / mean_gap if mean_gap else 0.0
        ur = statistics.pstdev(gaps) * 10 if len(gaps) > 1 else 0.0
        drift = mean_gap - self.tap_interval
        return bpm, ur, drift

    def _refresh(self) -> None:
        if not self.running:
            return
        now = time.perf_counter() * 1000.0
        if now < self.grid_start:
            left = (self.grid_start - now) / 1000.0
            self.beat.setText(t("trn.count_in_left", n=math.ceil(left)))
            return

        elapsed = (now - self.grid_start) / 1000.0
        remaining = max(0.0, self.seconds.value() - elapsed)
        taps = self._snapshot()
        bpm, _ur, _drift = self._rolling(taps)
        target = self.bpm.value()

        # Only notes that have already gone past are judged, otherwise the
        # ones still approaching would count as missed.
        window = hit_window(target)
        due = [n for n in self.notes if n <= now - window]
        self.result = pat.judge(due, self.openers,
                                [x[0] for x in taps], window)
        self.result.notes = len(self.notes)
        self.lane.set_judged(self.result.matched, self._press_marks(), True)

        if not bpm:
            tone = ""
        elif abs(bpm - target) > target * 0.08:
            tone = "bad"
        elif abs(bpm - target) > target * 0.03:
            tone = "warn"
        else:
            tone = "good"
        self.cards["bpm"].set_value(f"{bpm:.0f}" if bpm else "—", tone)
        hits = self.result.hits
        if hits:
            error = self.result.mean_error
            self.cards["error"].set_value(
                f"{error:+.1f}",
                "good" if abs(error) < window * 0.2 else "warn")
            self.cards["ur"].set_value(f"{self.result.ur:.0f}")
            self.cards["hits"].set_value(
                f"{hits}/{len(due)}",
                "bad" if self.result.misses > len(due) * 0.05 else "good")
        else:
            self.cards["error"].set_value("—")
            self.cards["ur"].set_value("—")
            self.cards["hits"].set_value("—")
        self.cards["left"].set_value(f"{remaining:.0f}")
        self.beat.setText("●" if int(elapsed * 1000 / self.beat_interval) % 2
                          else "○")

        # Redrawing the whole curve is the most expensive thing here, so
        # it happens a few times a second and only over the recent tail.
        if now - self.last_plot < PLOT_MS:
            return
        self.last_plot = now
        times = [x[0] for x in taps][-PLOT_POINTS:]
        if len(times) > 2:
            gaps = [times[i] - times[i - 1] for i in range(1, len(times))]
            self.curve.setData(list(range(len(gaps))), gaps)

    def _summarise(self) -> None:
        taps = self._snapshot()
        if len(taps) < 8 or not self.notes:
            self.summary.setText(t("trn.too_few"))
            return
        times = [x[0] for x in taps]
        hands = [x[1] for x in taps]
        gaps = [times[i] - times[i - 1] for i in range(1, len(times))]
        clean = [g for g in gaps if MIN_GAP_MS <= g < self.tap_interval * 4]
        bounced = sum(1 for g in gaps if g < MIN_GAP_MS)
        if len(clean) < 6:
            self.summary.setText(t("trn.too_few"))
            return

        window = hit_window(self.bpm.value())
        result = pat.judge(self.notes, self.openers, times, window)
        self.result = result

        switches = sum(1 for i in range(1, len(hands)) if hands[i] != hands[i - 1])
        alternation = switches / max(1, len(hands) - 1)
        bpm = 15000.0 / statistics.mean(clean)
        target = self.bpm.value()

        held = (result.accuracy >= 0.98 and result.ur < 180
                and abs(result.mean_error) < window * 0.25)
        text = t("trn.result_held" if held else "trn.result_missed",
                 bpm=bpm, target=target, ur=result.ur,
                 hits=result.hits, notes=result.notes,
                 acc=result.accuracy * 100, error=result.mean_error,
                 misses=result.misses, extras=result.extras,
                 alt=alternation * 100)

        # Entering a run late while carrying it on time is a different fault
        # from being late throughout, and it is the one bursts expose.
        gap = result.opener_gap
        if abs(gap) >= 8.0:
            text += "  " + t("trn.result_opener_late" if gap > 0
                             else "trn.result_opener_early", gap=abs(gap))

        if bounced and bounced >= len(gaps) * 0.02:
            key = "trn.result_stalled" if self.stalls[0] else "trn.result_noise"
            text += "  " + t(key, n=bounced, total=len(gaps), ms=MIN_GAP_MS,
                             stalls=self.stalls[0], worst=self.stalls[1])
        self.summary.setText(text)

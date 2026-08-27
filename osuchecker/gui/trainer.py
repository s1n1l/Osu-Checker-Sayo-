"""In-app tapping trainer: hold a tempo and see it fall apart in real time.

The metronome clicks once per musical beat while four taps are expected
between clicks, which is how a stream at a given BPM is normally counted.
Taps are read from the O3C through Raw Input, so what is measured is the
same signal the game receives.
"""
from __future__ import annotations

import math
import statistics
import struct
import time
import wave

import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (QCheckBox, QGridLayout, QHBoxLayout, QLabel,
                               QPushButton, QSpinBox, QVBoxLayout, QWidget)

from ..config import Config
from ..device.rawinput import RawKeyboardListener
from ..i18n import t
from ..paths import data_file
from . import theme

VK_NAMES = {0x50: "P", 0x56: "V", 0x42: "B"}
TAPS_PER_BEAT = 4
COUNT_IN_BEATS = 4
ROLL_TAPS = 16
SAMPLE_RATE = 44100


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
        self.down: set[str] = set()
        self.taps: list[tuple[float, str]] = []
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

        info = QLabel(t("trn.info"))
        info.setWordWrap(True)
        info.setObjectName("dim")
        root.addWidget(info)

        row = QHBoxLayout()
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
        root.addLayout(row)

        grid = QGridLayout()
        self.cards: dict[str, QLabel] = {}
        for column, (key, caption) in enumerate((
                ("bpm", t("trn.card_bpm")),
                ("ur", t("trn.card_ur")),
                ("drift", t("trn.card_drift")),
                ("left", t("trn.card_left")),
        )):
            caption_label = QLabel(caption)
            caption_label.setObjectName("dim")
            caption_label.setAlignment(Qt.AlignCenter)
            value = QLabel("—")
            value.setObjectName("huge" if key == "bpm" else "value")
            value.setAlignment(Qt.AlignCenter)
            grid.addWidget(caption_label, 0, column)
            grid.addWidget(value, 1, column)
            self.cards[key] = value
        root.addLayout(grid)

        self.beat = QLabel("")
        self.beat.setObjectName("h2")
        self.beat.setAlignment(Qt.AlignCenter)
        self.beat.setMinimumHeight(34)
        root.addWidget(self.beat)

        self.plot = pg.PlotWidget(title=t("trn.plot_title"))
        self.plot.setLabel("left", t("trn.plot_y"))
        self.plot.setLabel("bottom", t("trn.plot_x"))
        self.plot.setMinimumHeight(190)
        for name in ("left", "bottom"):
            self.plot.getAxis(name).enableAutoSIPrefix(False)
        self.curve = self.plot.plot(pen=pg.mkPen(theme.ACCENT, width=2))
        self.target_line = pg.InfiniteLine(pos=0, angle=0,
                                           pen=pg.mkPen("#66d9a6", width=1))
        self.plot.addItem(self.target_line)
        root.addWidget(self.plot, 1)

        self.summary = QLabel(t("trn.idle"))
        self.summary.setWordWrap(True)
        root.addWidget(self.summary)
        self._retarget()

        self.ticker = QTimer(self)
        self.ticker.setTimerType(Qt.PreciseTimer)
        self.ticker.setInterval(2)
        self.ticker.timeout.connect(self._tick)

        self.ui_timer = QTimer(self)
        self.ui_timer.setInterval(60)
        self.ui_timer.timeout.connect(self._refresh)

    def _retarget(self) -> None:
        interval = self.tap_interval
        self.target_line.setValue(interval)
        self.plot.setYRange(interval * 0.5, interval * 1.5)
        if not self.running:
            self.cards["bpm"].setText(f"{self.bpm.value()}")
            self.cards["bpm"].setStyleSheet(f"color: {theme.FG_DIM};")
            self.cards["ur"].setText("—")
            self.cards["drift"].setText("—")
            self.cards["left"].setText(f"{self.seconds.value()}")

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
        self.cfg.save()

        self.listener = RawKeyboardListener(on_key=self._on_key)
        if not self.listener.start():
            self.summary.setText(t("trn.no_device",
                                   message=self.listener.error or ""))
            return
        self.taps.clear()
        self.down.clear()
        self.running = True
        self.beat_index = -COUNT_IN_BEATS
        self.start_time = time.perf_counter() * 1000.0
        self.next_beat = self.start_time
        self.grid_start = self.start_time + COUNT_IN_BEATS * self.beat_interval
        self.btn.setText(t("trn.stop"))
        self.summary.setText(t("trn.count_in"))
        self._retarget()
        self.ticker.start()
        self.ui_timer.start()

    def stop(self) -> None:
        self.running = False
        self.ticker.stop()
        self.ui_timer.stop()
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.btn.setText(t("trn.start"))
        self.beat.setText("")
        self._summarise()

    def _on_key(self, stroke) -> None:
        name = VK_NAMES.get(stroke.vkey)
        if name is None or not self.running:
            return
        if not stroke.down:
            self.down.discard(name)
            return
        if name in self.down:
            return
        self.down.add(name)
        now = stroke.t * 1000.0
        if now >= self.grid_start:
            self.taps.append((now, name))

    def _tick(self) -> None:
        now = time.perf_counter() * 1000.0
        if now >= self.next_beat:
            if self.sound.isChecked():
                effect = self.accent if self.beat_index % 4 == 0 else self.click
                effect.play()
            self.beat_index += 1
            self.next_beat += self.beat_interval
        if now - self.grid_start >= self.seconds.value() * 1000.0:
            self.stop()

    def _rolling(self) -> tuple[float, float, float]:
        if len(self.taps) < 4:
            return 0.0, 0.0, 0.0
        times = [x[0] for x in self.taps]
        window = times[-ROLL_TAPS:]
        gaps = [window[i] - window[i - 1] for i in range(1, len(window))]
        gaps = [g for g in gaps if 0 < g < self.tap_interval * 4]
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
        bpm, ur, drift = self._rolling()
        self.cards["bpm"].setText(f"{bpm:.0f}" if bpm else "—")
        self.cards["ur"].setText(f"{ur:.0f}" if ur else "—")
        self.cards["drift"].setText(f"{drift:+.1f}" if bpm else "—")
        self.cards["left"].setText(f"{remaining:.0f}")

        target = self.bpm.value()
        colour = "#66d9a6" if abs(bpm - target) <= target * 0.03 else "#ffb84d"
        if bpm and abs(bpm - target) > target * 0.08:
            colour = "#ff5c5c"
        self.cards["bpm"].setStyleSheet(f"color: {colour};")
        self.beat.setText("●" if int(elapsed * 1000 / self.beat_interval) % 2
                          else "○")

        times = [x[0] for x in self.taps]
        if len(times) > 2:
            gaps = [times[i] - times[i - 1] for i in range(1, len(times))]
            self.curve.setData(list(range(len(gaps))), gaps)

    def _summarise(self) -> None:
        if len(self.taps) < 8:
            self.summary.setText(t("trn.too_few"))
            return
        times = [x[0] for x in self.taps]
        hands = [x[1] for x in self.taps]
        gaps = [times[i] - times[i - 1] for i in range(1, len(times))]
        clean = [g for g in gaps if 0 < g < self.tap_interval * 4]
        mean_gap = statistics.mean(clean)
        bpm = 15000.0 / mean_gap
        ur = statistics.pstdev(clean) * 10

        third = max(2, len(clean) // 3)
        early = statistics.mean(clean[:third])
        late = statistics.mean(clean[-third:])
        slowdown = (15000.0 / early) - (15000.0 / late)

        switches = sum(1 for i in range(1, len(hands)) if hands[i] != hands[i - 1])
        alternation = switches / max(1, len(hands) - 1)
        dropped = sum(1 for g in gaps if g > self.tap_interval * 1.6)

        target = self.bpm.value()
        held = (abs(bpm - target) <= target * 0.03 and dropped == 0
                and ur < 180)
        self.summary.setText(t("trn.result_held" if held else "trn.result_missed",
                               bpm=bpm, target=target, ur=ur, taps=len(times),
                               slowdown=slowdown, alt=alternation * 100,
                               dropped=dropped))

"""Replay playback: the playfield, the cursor and where each note went wrong.

Sliders are drawn as their head only. The path of a slider is not parsed,
and for tapping and aim analysis the head is the point that is judged.

The clock shown here is the one the analysis uses, so if the replay needed
a correction to line up with the beatmap (see replay.align) the correction
is already in it and the banner says so.
"""
from __future__ import annotations

import time

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QPushButton,
                               QSlider, QVBoxLayout, QWidget)

from ..analysis.aim import circle_radius
from ..analysis.judge import JUDGE_50, JUDGE_100, JUDGE_300, JUDGE_MISS
from ..analysis.pipeline import Analysis
from ..i18n import t
from . import theme
from .widgets import Banner, muted_label

COL_LEFT = theme.HAND_LEFT
COL_RIGHT = theme.HAND_RIGHT

FIELD_W, FIELD_H = 512.0, 384.0
TRAIL_MS = 420.0
SPEEDS = (0.1, 0.25, 0.5, 1.0)
STEP_MS = 1000.0
BIG_STEP_MS = 5000.0
# The marker on the strip below only has to look continuous, and moving it
# is what forces the strip to repaint. At 60 Hz that repaint was three
# quarters of the cost of a frame.
NAV_MS = 50.0

JUDGE_COLOR = {
    JUDGE_300: (110, 190, 255),
    JUDGE_100: (61, 220, 151),
    JUDGE_50: (255, 180, 84),
    JUDGE_MISS: (255, 95, 109),
}
UPCOMING = (150, 150, 160)


def approach_preempt(ar: float) -> float:
    if ar < 5:
        return 1200.0 + 600.0 * (5.0 - ar) / 5.0
    if ar > 5:
        return 1200.0 - 750.0 * (ar - 5.0) / 5.0
    return 1200.0


class PlaybackView(QWidget):
    seeked = Signal(float)

    def __init__(self):
        super().__init__()
        self.analysis: Analysis | None = None
        self.time_ms = 0.0
        self.duration = 0.0
        self.speed = 1.0
        self.playing = False
        self._objects: list = []
        self._obj_times = np.zeros(0)
        self._judge_by_index: dict = {}
        self._ct = np.zeros(0)
        self._cx = np.zeros(0)
        self._cy = np.zeros(0)
        self._key_spans: list[tuple[float, float, str]] = []
        self._extras: list[float] = []
        self._radius = 32.0
        self._preempt = 1200.0
        # Where every press landed on the playfield, so the path shows what
        # was pressed and not just where the cursor went.
        self._press_t = np.zeros(0)
        self._press_x = np.zeros(0)
        self._press_y = np.zeros(0)
        self._press_side: list[str] = []
        self._press_extra: list[bool] = []
        self._last_frame = 0.0
        self._last_nav = -1e9
        self._pen_cache: dict = {}
        self._brush_cache: dict = {}

        # Space and the arrow keys are handled here, so the view has to be
        # able to take focus and keep it away from the buttons.
        self.setFocusPolicy(Qt.StrongFocus)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        self.banner = Banner()
        self.banner.setVisible(False)
        root.addWidget(self.banner)

        self.plot = pg.PlotWidget()
        self.plot.setAspectLocked(True)
        self.plot.getViewBox().invertY(True)
        self.plot.getViewBox().setBackgroundColor(theme.BG_INPUT)
        self.plot.setXRange(-20, FIELD_W + 20, padding=0)
        self.plot.setYRange(-20, FIELD_H + 20, padding=0)
        self.plot.hideAxis("left")
        self.plot.hideAxis("bottom")
        self.plot.setMouseEnabled(False, False)
        self.plot.setMenuEnabled(False)
        self.plot.setFocusPolicy(Qt.NoFocus)
        root.addWidget(self.plot, 1)

        border = pg.PlotCurveItem([0, FIELD_W, FIELD_W, 0, 0],
                                  [0, 0, FIELD_H, FIELD_H, 0],
                                  pen=pg.mkPen(theme.LINE, width=1))
        self.plot.addItem(border)
        self.approach = pg.ScatterPlotItem(pxMode=False, brush=None)
        self.plot.addItem(self.approach)
        self.circles = pg.ScatterPlotItem(pxMode=False)
        self.plot.addItem(self.circles)
        self.trail = pg.PlotCurveItem(pen=pg.mkPen("#ffe066", width=2),
                                      antialias=True)
        self.plot.addItem(self.trail)
        # One dot per press on the path, in the colour of the hand.
        self.presses = pg.ScatterPlotItem(pxMode=True)
        self.plot.addItem(self.presses)
        self.hold_ring = pg.ScatterPlotItem(size=22, brush=None)
        self.plot.addItem(self.hold_ring)
        self.cursor = pg.ScatterPlotItem(size=11, brush=pg.mkBrush("#ffffff"),
                                         pen=pg.mkPen("#000000", width=1))
        self.plot.addItem(self.cursor)
        self.link = pg.PlotCurveItem(pen=pg.mkPen(theme.BAD, width=2,
                                                  style=Qt.DashLine))
        self.plot.addItem(self.link)

        self.nav = pg.PlotWidget()
        self.nav.setMaximumHeight(120)
        theme.style_plot(self.nav)
        self.nav.setLabel("left", t("plot.timeline_y"),
                          **theme.plot_label_style())
        self.nav.setMouseEnabled(False, False)
        self.nav.setMenuEnabled(False)
        self.nav.setFocusPolicy(Qt.NoFocus)
        self.nav.scene().sigMouseClicked.connect(self._nav_clicked)
        self.nav_marker = pg.InfiniteLine(pos=0, angle=90,
                                          pen=pg.mkPen("#ffffff", width=1))
        self.nav.addItem(self.nav_marker)
        root.addWidget(self.nav)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.btn_play = QPushButton(t("pb.play"))
        self.btn_play.setObjectName("primary")
        self.btn_play.setMinimumWidth(110)
        self.btn_play.setFocusPolicy(Qt.NoFocus)
        self.btn_play.clicked.connect(self.toggle)
        controls.addWidget(self.btn_play)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.sliderMoved.connect(self._slider_moved)
        self.slider.sliderPressed.connect(lambda: self.pause())
        controls.addWidget(self.slider, 1)

        self.clock = QLabel("00:00.000")
        self.clock.setObjectName("mono")
        controls.addWidget(self.clock)

        self.speed_box = QComboBox()
        self.speed_box.setFocusPolicy(Qt.NoFocus)
        for value in SPEEDS:
            self.speed_box.addItem(f"{value:g}×", value)
        self.speed_box.setCurrentIndex(len(SPEEDS) - 1)
        self.speed_box.currentIndexChanged.connect(self._speed_changed)
        controls.addWidget(self.speed_box)

        self.jump = QComboBox()
        self.jump.setMinimumWidth(320)
        self.jump.setFocusPolicy(Qt.NoFocus)
        self.jump.currentIndexChanged.connect(self._jump_changed)
        controls.addWidget(self.jump)
        root.addLayout(controls)

        self.readout = QLabel("")
        self.readout.setObjectName("mono")
        root.addWidget(self.readout)
        root.addWidget(muted_label(t("pb.keys_hint")))
        root.addWidget(muted_label(t("pb.legend")))

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)

    # keyboard -----------------------------------------------------------

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key == Qt.Key_Space:
            self.toggle()
            event.accept()
            return
        if key in (Qt.Key_Left, Qt.Key_Right):
            step = BIG_STEP_MS if event.modifiers() & Qt.ShiftModifier else STEP_MS
            self.pause()
            self.seek(self.time_ms + (step if key == Qt.Key_Right else -step))
            event.accept()
            return
        super().keyPressEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.setFocus(Qt.OtherFocusReason)

    def mousePressEvent(self, event) -> None:
        self.setFocus(Qt.MouseFocusReason)
        super().mousePressEvent(event)

    # data ---------------------------------------------------------------

    def set_analysis(self, a: Analysis) -> None:
        self.pause()
        self.analysis = a
        self.jump.blockSignals(True)
        self.jump.clear()
        if a.judge is None or a.beatmap is None:
            self.jump.blockSignals(False)
            self.banner.set_text("", "info")
            return

        if a.alignment.suspect:
            self.banner.set_text(t("align.suspect_playback",
                                   pct=a.alignment.coverage * 100), "warn")
        elif a.alignment.source == "search" and a.alignment.corrected:
            self.banner.set_text(t("align.searched",
                                   sec=a.alignment.shift / 1000.0,
                                   pct=a.alignment.coverage * 100), "warn")
        elif a.alignment.corrected:
            self.banner.set_text(t("align.corrected_playback",
                                   sec=a.alignment.shift / 1000.0), "info")
        else:
            self.banner.set_text("", "info")

        self._objects = [o for o in a.beatmap.hit_objects
                         if o.kind in ("circle", "slider")]
        self._obj_times = np.array([o.time for o in self._objects], dtype=float)
        self._judge_by_index = {j.index: j for j in a.judge.judgements}
        self._radius = circle_radius(a.beatmap.cs, a.replay.mods)
        ar = a.beatmap.ar
        if a.replay.mods & 16:
            ar = min(10.0, ar * 1.4)
        elif a.replay.mods & 2:
            ar = ar * 0.5
        self._preempt = approach_preempt(ar)

        frames = a.replay.frames
        self._ct = np.array([f[0] for f in frames], dtype=float)
        self._cx = np.array([f[1] for f in frames], dtype=float)
        self._cy = np.array([f[2] for f in frames], dtype=float)
        if a.replay.mods & 16:
            self._cy = FIELD_H - self._cy

        self._key_spans = [(e.press, e.release, e.key)
                           for e in a.replay.key_events
                           if e.key in ("left", "right")]
        self._extras = [e.time for e in a.judge.extras]
        self.duration = float(self._ct[-1]) if len(self._ct) else 0.0

        extras = set(self._extras)
        presses = sorted((e.press, e.key) for e in a.replay.key_events
                         if e.key in ("left", "right"))
        self._press_t = np.array([p for p, _ in presses], dtype=float)
        self._press_side = [k for _, k in presses]
        self._press_extra = [p in extras for p, _ in presses]
        if len(self._press_t):
            self._press_x = np.interp(self._press_t, self._ct, self._cx)
            self._press_y = np.interp(self._press_t, self._ct, self._cy)
        else:
            self._press_x = self._press_y = np.zeros(0)

        self.jump.addItem(t("pb.jump_placeholder"), -1.0)
        for episode in a.episodes:
            self.jump.addItem(
                f"{episode.time_label}  {episode.cause_label}  "
                f"{episode.loss_label}", float(episode.start) - 1200.0)
        self.jump.blockSignals(False)

        self._draw_nav(a)
        self.seek(self._objects[0].time - 1500 if self._objects else 0.0)

    def _draw_nav(self, a: Analysis) -> None:
        self.nav.clear()
        self.nav.addItem(pg.InfiniteLine(pos=0, angle=0,
                                         pen=pg.mkPen(theme.FG_MUTED)))
        for judgement, color in JUDGE_COLOR.items():
            points = [(j.obj.time / 1000.0,
                       j.error if j.error is not None else 0.0)
                      for j in a.judge.judgements if j.judgement == judgement]
            if not points:
                continue
            xs, ys = zip(*points)
            size = 6 if judgement == JUDGE_MISS else 3
            self.nav.addItem(pg.ScatterPlotItem(
                xs, ys, size=size, pen=None, brush=pg.mkBrush(*color)))
        self.nav_marker = pg.InfiniteLine(pos=0, angle=90,
                                          pen=pg.mkPen("#ffffff", width=1))
        self.nav.addItem(self.nav_marker)

        # Fixed ranges, autorange off. Otherwise every move of the marker
        # re-ranges the view, which repaints both axes through a QPicture --
        # three quarters of the cost of a playback frame.
        errors = [abs(j.error) for j in a.judge.judgements
                  if j.error is not None]
        limit = max(a.judge.windows["50"], max(errors) if errors else 0.0)
        box = self.nav.getViewBox()
        box.setXRange(0.0, max(1.0, self.duration / 1000.0), padding=0.02)
        box.setYRange(-limit * 1.05, limit * 1.05, padding=0)
        box.disableAutoRange()

    def _pen(self, colour, alpha, width=2):
        key = (colour, alpha, width)
        pen = self._pen_cache.get(key)
        if pen is None:
            pen = self._pen_cache[key] = pg.mkPen(*colour, alpha, width=width)
        return pen

    def _brush(self, colour, alpha):
        key = (colour, alpha)
        brush = self._brush_cache.get(key)
        if brush is None:
            brush = self._brush_cache[key] = pg.mkBrush(*colour, alpha)
        return brush

    # transport ----------------------------------------------------------

    def toggle(self) -> None:
        self.pause() if self.playing else self.play()

    def play(self) -> None:
        if self.duration <= 0:
            return
        self.playing = True
        self._last_frame = time.perf_counter()
        self.btn_play.setText(t("pb.pause"))
        self.timer.start()

    def pause(self) -> None:
        self.playing = False
        self.btn_play.setText(t("pb.play"))
        self.timer.stop()

    def seek(self, ms: float) -> None:
        self.time_ms = max(0.0, min(ms, self.duration))
        self._render()

    def _slider_moved(self, value: int) -> None:
        if self.duration > 0:
            self.seek(self.duration * value / 1000.0)

    def _speed_changed(self, index: int) -> None:
        self.speed = self.speed_box.itemData(index)

    def _jump_changed(self, index: int) -> None:
        target = self.jump.itemData(index)
        if target is not None and target >= 0:
            self.pause()
            self.seek(target)
            self.setFocus(Qt.OtherFocusReason)

    def _nav_clicked(self, event) -> None:
        if self.duration <= 0:
            return
        point = self.nav.getPlotItem().vb.mapSceneToView(event.scenePos())
        self.pause()
        self.seek(point.x() * 1000.0)

    def _tick(self) -> None:
        # Advance by the time that actually passed. Adding a fixed 16 ms per
        # timer tick means a slow frame silently slows the replay down.
        now = time.perf_counter()
        step = (now - self._last_frame) * 1000.0
        self._last_frame = now
        self.seek(self.time_ms + min(step, 250.0) * self.speed)
        if self.time_ms >= self.duration:
            self.pause()

    # drawing ------------------------------------------------------------

    def _render(self) -> None:
        if self.analysis is None or not len(self._ct):
            return
        now = self.time_ms

        lo = int(np.searchsorted(self._obj_times, now - 400.0))
        hi = int(np.searchsorted(self._obj_times, now + self._preempt))
        spots, approach = [], []
        for index in range(lo, hi):
            obj = self._objects[index]
            judgement = self._judge_by_index.get(index)
            color = UPCOMING
            if judgement is not None and obj.time <= now:
                color = JUDGE_COLOR.get(judgement.judgement, UPCOMING)
            alpha = 255
            if obj.time < now:
                alpha = int(max(0, 255 * (1.0 - (now - obj.time) / 400.0)))
            y = FIELD_H - obj.y if self.analysis.replay.mods & 16 else obj.y
            # Pens and brushes are cached: building them per spot per frame
            # allocates a few thousand Qt objects a second for nothing.
            spots.append({"pos": (obj.x, y), "size": self._radius * 2,
                          "brush": self._brush(color, min(alpha, 90)),
                          "pen": self._pen(color, alpha)})
            if obj.time > now:
                scale = 1.0 + 3.0 * (obj.time - now) / self._preempt
                approach.append({"pos": (obj.x, y),
                                 "size": self._radius * 2 * scale,
                                 "brush": None,
                                 "pen": self._pen(UPCOMING, 120, 1)})
        self.circles.setData(spots)
        self.approach.setData(approach)

        px = float(np.interp(now, self._ct, self._cx))
        py = float(np.interp(now, self._ct, self._cy))
        self.cursor.setData([px], [py])

        start = int(np.searchsorted(self._ct, now - TRAIL_MS))
        end = int(np.searchsorted(self._ct, now))
        if end > start:
            # The cursor is where it is now, so the trail ends there rather
            # than at the last frame the replay happened to record.
            self.trail.setData(np.append(self._cx[start:end], px),
                               np.append(self._cy[start:end], py))
        else:
            self.trail.setData([], [])

        held = [key for press, release, key in self._key_spans
                if press <= now <= release]
        if held:
            colour = COL_LEFT if "left" in held else COL_RIGHT
            self.hold_ring.setData([px], [py], size=22, brush=None,
                                   pen=pg.mkPen(colour, width=2))
        else:
            self.hold_ring.setData([], [])

        lo = int(np.searchsorted(self._press_t, now - TRAIL_MS))
        hi = int(np.searchsorted(self._press_t, now, side="right"))
        marks = []
        for i in range(lo, hi):
            age = (now - self._press_t[i]) / TRAIL_MS
            alpha = int(max(40, 235 * (1.0 - age)))
            colour = (COL_LEFT if self._press_side[i] == "left"
                      else COL_RIGHT)
            marks.append({
                "pos": (self._press_x[i], self._press_y[i]), "size": 9,
                "brush": pg.mkBrush(QColor(colour).red(),
                                    QColor(colour).green(),
                                    QColor(colour).blue(), alpha),
                "pen": (pg.mkPen(theme.BAD, width=2)
                        if self._press_extra[i] else None)})
        self.presses.setData(marks)

        nearest = None
        if len(self._obj_times):
            index = int(np.argmin(np.abs(self._obj_times - now)))
            if abs(self._obj_times[index] - now) < 400.0:
                nearest = index
        if nearest is not None:
            obj = self._objects[nearest]
            y = FIELD_H - obj.y if self.analysis.replay.mods & 16 else obj.y
            self.link.setData([px, obj.x], [py, y])
        else:
            self.link.setData([], [])

        if abs(now - self._last_nav) >= NAV_MS:
            self._last_nav = now
            self.nav_marker.setValue(now / 1000.0)
        if not self.slider.isSliderDown() and self.duration > 0:
            self.slider.blockSignals(True)
            self.slider.setValue(int(1000 * now / self.duration))
            self.slider.blockSignals(False)
        self.clock.setText(f"{int(now // 60000):02d}:{int(now // 1000) % 60:02d}"
                           f".{int(now) % 1000:03d}")
        self.readout.setText(self._describe(now, nearest, px, py))

    def _describe(self, now: float, nearest: int | None,
                  px: float, py: float) -> str:
        held = [key for press, release, key in self._key_spans
                if press <= now <= release]
        keys = "".join(
            f"[{t('hand.' + side).upper()}]" if side in held else "[ ]"
            for side in ("left", "right"))
        parts = [f"{keys}"]

        if nearest is not None:
            judgement = self._judge_by_index.get(nearest)
            obj = self._objects[nearest]
            y = FIELD_H - obj.y if self.analysis.replay.mods & 16 else obj.y
            distance = float(np.hypot(px - obj.x, py - y))
            parts.append(t("pb.distance", px=distance,
                           frac=distance / self._radius))
            if judgement is not None and judgement.error is not None:
                parts.append(t("pb.error", ms=judgement.error))
            elif judgement is not None and judgement.judgement == JUDGE_MISS:
                parts.append(t("pb.miss"))

        recent = [x for x in self._extras if now - 250.0 <= x <= now]
        if recent:
            parts.append(t("pb.extra"))
        return "   ".join(parts)

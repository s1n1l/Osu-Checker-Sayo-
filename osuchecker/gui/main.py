"""Main application window."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
    QProgressBar, QPushButton, QScrollArea, QSpinBox, QSplitter,
    QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget)

from ..analysis.episodes import (CAUSE_AIM, CAUSE_EARLY, CAUSE_LATE,
                                 CAUSE_SCATTER)
from ..analysis.judge import JUDGE_50, JUDGE_100, JUDGE_300
from ..analysis.pipeline import Analysis, analyse
from ..analysis.tapping import interval_histogram
from ..analysis.training import find_practice_maps, scan_maps
from ..config import Config
from ..device.keys import NUM_KEYS, key_name
from ..i18n import LANGUAGES, set_language, t
from ..paths import resource_path
from ..recorder import Session, SessionRecorder
from ..replay.index import BeatmapIndex
from . import theme
from .playback import PlaybackView
from .trainer import TrainerTab
from .widgets import (Badge, Banner, Card, KeyCaptureButton, StatTile,
                      dim_label, muted_label, rich_text, section_label)

ASSETS = resource_path("assets")
COL_LEFT = theme.HAND_LEFT
COL_RIGHT = theme.HAND_RIGHT
SEV_COLOR = theme.SEVERITY
CAUSE_COLOR = {CAUSE_LATE: theme.BAD, CAUSE_EARLY: theme.WARN,
               CAUSE_SCATTER: "#c792ea", CAUSE_AIM: theme.GOOD}
JUDGE_COLOR = {JUDGE_300: theme.HAND_LEFT, JUDGE_100: theme.GOOD,
               JUDGE_50: theme.WARN}
PRIORITY_COLOR = {1: theme.BAD, 2: theme.WARN}


def app_icon() -> QIcon:
    path = ASSETS / "icon.ico"
    return QIcon(str(path)) if path.exists() else QIcon()


class AnalyseWorker(QThread):
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, path: str, index: BeatmapIndex, cfg: Config,
                 device: dict | None = None):
        super().__init__()
        self.path, self.index, self.cfg = path, index, cfg
        self.device = device

    def run(self):
        try:
            self.done.emit(analyse(self.path, self.index, self.cfg,
                                   device=self.device))
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")


class IndexWorker(QThread):
    progress = Signal(int, int, str)
    done = Signal(int)

    def __init__(self, index: BeatmapIndex, songs: str, lazer: str):
        super().__init__()
        self.index, self.songs, self.lazer = index, songs, lazer

    def run(self):
        n = 0
        if self.songs:
            n += self.index.scan_stable_songs(
                self.songs, lambda i, total, s: self.progress.emit(i, total, s))
        if self.lazer:
            n += self.index.scan_lazer_files(
                self.lazer, lambda i, total, s: self.progress.emit(i, total, s))
        self.index.save()
        self.done.emit(n)


class MapScanWorker(QThread):
    progress = Signal(int, int, str)
    done = Signal(object)

    def __init__(self, paths: list[str]):
        super().__init__()
        self.paths = paths

    def run(self):
        self.done.emit(scan_maps(
            self.paths,
            lambda i, total, s: self.progress.emit(i, total, s)))


class DropArea(QFrame):
    dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(74)
        self._paint(False)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        label = QLabel(t("analysis.drop_hint"))
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("dim")
        lay.addWidget(label)

    def _paint(self, active: bool) -> None:
        colour = theme.ACCENT if active else theme.LINE
        self.setStyleSheet(
            f"QFrame {{ border: 1px dashed {colour}; border-radius: 10px;"
            f" background: {theme.BG_PANEL if active else 'transparent'}; }}")

    def dragEnterEvent(self, event):
        if any(u.toLocalFile().lower().endswith(".osr")
               for u in event.mimeData().urls()):
            event.acceptProposedAction()
            self._paint(True)

    def dragLeaveEvent(self, event):
        self._paint(False)

    def dropEvent(self, event):
        self._paint(False)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".osr"):
                self.dropped.emit(path)
                break


def make_table(headers: list[str], max_height: int | None = None) -> QTableWidget:
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.horizontalHeader().setHighlightSections(False)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionMode(QTableWidget.NoSelection)
    if max_height:
        # Kept so fill_table can shrink a short table to its rows instead of
        # leaving a slab of empty grid under them.
        table.setProperty("height_cap", max_height)
        table.setMaximumHeight(max_height)
    return table


def fill_table(table: QTableWidget, rows: list[list],
               colors: dict[tuple[int, int], str] | None = None) -> None:
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            if colors and (r, c) in colors:
                item.setForeground(QColor(colors[(r, c)]))
            table.setItem(r, c, item)
    cap = table.property("height_cap")
    if cap:
        content = (table.horizontalHeader().height() + 4
                   + sum(table.rowHeight(r) for r in range(len(rows))))
        table.setMaximumHeight(min(int(cap), content))


def scroll_column(spacing: int = 12) -> tuple[QScrollArea, QVBoxLayout]:
    """A vertically scrolling column of cards."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    inner = QWidget()
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(0, 0, 8, 0)
    lay.setSpacing(spacing)
    area.setWidget(inner)
    return area, lay


def clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()


def alignment_note(a: Analysis) -> tuple[str, str]:
    """Banner text for how the replay clock lined up with the beatmap."""
    al = a.alignment
    if al.suspect:
        return t("align.suspect", pct=al.coverage * 100), "warn"
    if al.source == "search" and al.corrected:
        return t("align.searched", sec=al.shift / 1000.0,
                 pct=al.coverage * 100), "warn"
    if al.corrected:
        return t("align.corrected", sec=al.shift / 1000.0,
                 pct=al.coverage * 100), "info"
    return "", "info"


class OverviewView(QWidget):
    """Findings first, then the two plots the findings are drawn from."""

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        self.banner = Banner()
        self.banner.setVisible(False)
        lay.addWidget(self.banner)

        split = QSplitter(Qt.Horizontal)

        left = Card(t("ov.findings_title"))
        self.summary = muted_label("")
        left.add(self.summary)
        self.findings = rich_text(flat=True)
        left.add(self.findings, 1)
        split.addWidget(left)

        right = QWidget()
        col = QVBoxLayout(right)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(10)

        self.hist = pg.PlotWidget()
        theme.style_plot(self.hist, title=t("plot.hist_title"))
        self.hist.setLabel("bottom", t("plot.hist_x"), **theme.plot_label_style())
        col.addWidget(self.hist, 3)
        self.hist_hint = muted_label(t("plot.hist_hint"))
        col.addWidget(self.hist_hint)

        self.timeline = pg.PlotWidget()
        theme.style_plot(self.timeline, title=t("plot.timeline_title"))
        self.timeline.setLabel("bottom", t("plot.timeline_x"),
                               **theme.plot_label_style())
        self.timeline.setLabel("left", t("plot.timeline_y"),
                               **theme.plot_label_style())
        col.addWidget(self.timeline, 3)
        self.timeline_hint = muted_label(t("plot.timeline_hint"))
        col.addWidget(self.timeline_hint)

        col.addWidget(section_label(t("ov.table_title")))
        self.table = make_table(
            [t("col.bpm"), t("col.notes"), t("col.error"), t("col.ur"),
             t("col.drift"), t("col.misses"), t("col.extras")], 170)
        col.addWidget(self.table)
        col.addWidget(muted_label(t("ov.table_hint")))
        split.addWidget(right)
        split.setSizes([500, 740])
        lay.addWidget(split, 1)

    def render(self, a: Analysis):
        self.findings.clear()
        self.hist.clear()
        self.timeline.clear()
        self.table.setRowCount(0)

        text, kind = alignment_note(a)
        self.banner.set_text(text, kind)

        if a.judge is None:
            self.summary.setText("")
            return

        counts = {"high": 0, "medium": 0, "info": 0}
        for f in a.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        self.summary.setText(t("ov.summary", high=counts["high"],
                               medium=counts["medium"], info=counts["info"]))

        html = []
        for f in a.findings:
            color = SEV_COLOR.get(f.severity, theme.FG_DIM)
            block = (f"<div class='block'>"
                     f"<span class='kicker' style='color:{color}'>"
                     f"{f.severity_label} · {f.area_label}</span><br>"
                     f"<span class='title'>{f.title}</span><br>"
                     f"<span class='lead'>{f.detail}</span>")
            if f.action:
                block += (f"<br><span class='action'>→ {t('ov.fix')} "
                          f"{f.action}</span>")
            html.append(block + "</div>")
        html.append(f"<div class='block'><br>"
                    f"<span class='kicker' style='color:{theme.FG_DIM}'>"
                    f"{t('ov.legend_title')}</span><br>"
                    f"<span class='lead'>{t('ov.legend_body')}</span></div>")
        self.findings.setHtml("".join(html))

        limit = max(20.0, a.judge.windows["50"])
        self.hist.addLegend(offset=(-10, 10), labelTextColor=theme.FG_DIM)
        for key, color, name in (("left", COL_LEFT, t("hand.left")),
                                 ("right", COL_RIGHT, t("hand.right"))):
            errors = a.judge.errors(key)
            if len(errors) < 5:
                continue
            values, edges = np.histogram(np.clip(errors, -limit, limit),
                                         bins=48, range=(-limit, limit))
            centers = (edges[:-1] + edges[1:]) / 2
            self.hist.addItem(pg.PlotCurveItem(
                centers, values, pen=pg.mkPen(color, width=2), name=name,
                fillLevel=0, brush=pg.mkBrush(QColor(color).darker(280))))
        for window, color in (("300", theme.GOOD), ("100", theme.WARN)):
            for sign in (-1, 1):
                self.hist.addItem(pg.InfiniteLine(
                    pos=sign * a.judge.windows[window], angle=90,
                    pen=pg.mkPen(color, style=Qt.DashLine)))
        self.hist.addItem(pg.InfiniteLine(
            pos=0, angle=90, pen=pg.mkPen(theme.FG_MUTED, style=Qt.DotLine)))

        for key, color in (("left", COL_LEFT), ("right", COL_RIGHT)):
            points = [(j.press_time / 1000.0, j.error)
                      for j in a.judge.judgements
                      if j.error is not None and j.key == key]
            if points:
                xs, ys = zip(*points)
                self.timeline.addItem(pg.ScatterPlotItem(
                    xs, ys, size=3, pen=None, brush=pg.mkBrush(color)))
        self.timeline.addItem(pg.InfiniteLine(pos=0, angle=0,
                                              pen=pg.mkPen(theme.FG_MUTED)))

        rows, colors = [], {}
        for r, b in enumerate([x for x in a.buckets if x.n_notes >= 20]):
            rows.append([f"{b.bpm:.0f}", b.n_notes, f"{b.mean_error:+.1f}",
                         f"{b.ur:.0f}", f"{b.mean_drift:+.1f}",
                         f"{b.miss_rate * 100:.1f}%",
                         f"{b.extra_rate * 100:.1f}%"])
            if b.mean_drift >= 8:
                colors[(r, 4)] = theme.BAD
            if b.extra_rate >= 0.02:
                colors[(r, 6)] = theme.WARN
        fill_table(self.table, rows, colors)


class AimView(QWidget):
    """Where the cursor sat when each note was pressed."""

    def __init__(self):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(11, 11, 11, 11)
        lay.setSpacing(12)

        left = QWidget()
        lcol = QVBoxLayout(left)
        lcol.setContentsMargins(0, 0, 0, 0)
        lcol.setSpacing(8)
        self.banner = Banner()
        self.banner.setVisible(False)
        lcol.addWidget(self.banner)
        self.plot = pg.PlotWidget()
        theme.style_plot(self.plot, grid=False, title=t("aim.plot_title"))
        self.plot.setAspectLocked(True)
        self.plot.setLabel("bottom", t("aim.axis_px"), **theme.plot_label_style())
        lcol.addWidget(self.plot, 1)
        self.legend = muted_label(t("aim.plot_legend"))
        lcol.addWidget(self.legend)
        lay.addWidget(left, 3)

        area, col = scroll_column()

        self.summary_card = Card(t("aim.summary_title"))
        self.summary = rich_text(flat=True, auto_height=True)
        self.summary_card.add(self.summary)
        col.addWidget(self.summary_card)

        help_card = Card(t("aim.help_title"))
        help_body = rich_text(flat=True, auto_height=True)
        help_body.setHtml(f"<span class='lead'>{t('aim.help_body')}</span>")
        help_card.add(help_body)
        col.addWidget(help_card)

        jump_card = Card(t("aim.by_jump"), t("aim.by_jump_hint"))
        self.by_jump = make_table(
            [t("aim.col_jump"), t("aim.col_notes"), t("aim.col_spread"),
             t("aim.col_edge"), t("aim.col_over"), t("aim.col_over_pct"),
             t("aim.col_speed"), t("aim.col_settle")], 170)
        jump_card.add(self.by_jump)
        col.addWidget(jump_card)

        dir_card = Card(t("aim.by_dir"), t("aim.by_dir_hint"))
        self.by_dir = make_table(
            [t("aim.col_dir"), t("aim.col_notes"), t("aim.col_spread"),
             t("aim.col_over")], 190)
        dir_card.add(self.by_dir)
        col.addWidget(dir_card)
        col.addStretch(1)
        lay.addWidget(area, 2)

    def render(self, a: Analysis):
        MS = t("unit.ms")
        self.plot.clear()
        self.summary.clear()
        text, kind = alignment_note(a)
        self.banner.set_text(text, kind)

        aim = a.aim
        if not aim or not aim.hits:
            self.summary.setHtml(f"<p>{t('aim.no_data')}</p>")
            return

        radius = aim.radius
        angles = np.linspace(0, 2 * np.pi, 180)
        for value, color, dash in ((radius, theme.ACCENT, Qt.SolidLine),
                                   (radius * 0.75, theme.FG_MUTED, Qt.DashLine)):
            self.plot.addItem(pg.PlotCurveItem(
                value * np.cos(angles), value * np.sin(angles),
                pen=pg.mkPen(color, width=2, style=dash)))
        for judgement in (JUDGE_300, JUDGE_100, JUDGE_50):
            sel = [h for h in aim.hits if h.judgement == judgement]
            if not sel:
                continue
            color = QColor(JUDGE_COLOR[judgement])
            self.plot.addItem(pg.ScatterPlotItem(
                [h.dx for h in sel], [-h.dy for h in sel], size=4, pen=None,
                brush=pg.mkBrush(color.red(), color.green(), color.blue(), 110)))
        bias_x, bias_y = aim.bias
        self.plot.addItem(pg.ScatterPlotItem(
            [bias_x], [-bias_y], size=17, symbol="+",
            pen=pg.mkPen("#ffe066", width=3)))
        span = radius * 2.5
        self.plot.setXRange(-span, span, padding=0)
        self.plot.setYRange(-span, span, padding=0)

        outside_class = "warn" if aim.outside_rate > 0.10 else "dim"
        self.summary.setHtml(
            f"<p><b>{t('aim.radius')}:</b> {radius:.1f} px</p>"
            f"<p><b>{t('aim.bias')}:</b> x {bias_x:+.1f} px, "
            f"y {bias_y:+.1f} px<br>"
            f"<span class='muted'>{t('aim.bias_hint')}</span></p>"
            f"<p><b>{t('aim.spread')}:</b> "
            f"{t('aim.spread_value', value=aim.spread)}<br>"
            f"<span class='muted'>{t('aim.spread_hint')}</span></p>"
            f"<p><b>{t('aim.edge')}:</b> {aim.edge_rate * 100:.1f}%<br>"
            f"<span class='muted'>{t('aim.edge_hint')}</span></p>"
            f"<p><b>{t('aim.outside')}:</b> "
            f"<span class='{outside_class}'>{aim.outside_rate * 100:.1f}%</span>"
            f"<br><span class='muted'>"
            f"{t('aim.outside_hint', px=aim.outside_blur, ms=aim.frame_ms)}"
            f"</span></p>"
            f"<p><b>{t('aim.overshoot')}:</b> "
            f"{t('aim.overshoot_value', px=aim.mean_overshoot, pct=aim.overshoot_rate * 100)}"
            f"<br><span class='muted'>{t('aim.overshoot_hint')}</span></p>"
            f"<p><b>{t('aim.speed')}:</b> "
            f"{t('aim.speed_value', v=aim.mean_speed)}<br>"
            f"<b>{t('aim.settle')}:</b> {aim.median_settle:.0f} {MS}<br>"
            f"<b>{t('aim.on_arrival')}:</b> "
            f"{aim.on_arrival_rate * 100:.0f}%<br>"
            f"<span class='muted'>{t('aim.on_arrival_hint')}</span></p>")

        rows, colors = [], {}
        for i, b in enumerate(aim.by_jump_size()):
            high = "∞" if b["hi"] > 1e8 else f"{b['hi']:.0f}"
            rows.append([f"{b['lo']:.0f}–{high}", b["n"], f"{b['spread']:.2f}",
                         f"{b['edge_rate'] * 100:.1f}%", f"{b['overshoot']:.1f}",
                         f"{b['overshoot_rate'] * 100:.0f}%",
                         f"{b['speed']:.2f}", f"{b['settle']:.0f}"])
            if b["edge_rate"] > 0.12:
                colors[(i, 3)] = theme.BAD
            if b["overshoot_rate"] > 0.30:
                colors[(i, 5)] = theme.WARN
        fill_table(self.by_jump, rows, colors)
        fill_table(self.by_dir,
                   [[d["name"], d["n"], f"{d['spread']:.2f}",
                     f"{d['overshoot']:.1f}"] for d in aim.by_direction()])


class EpisodesView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.addWidget(dim_label(t("ep.head")))
        self.table = make_table(
            [t("ep.col_time"), t("ep.col_tempo"), t("ep.col_notes"),
             t("ep.col_loss"), t("ep.col_cause"), t("ep.col_what")])
        header = self.table.horizontalHeader()
        for c in range(5):
            header.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        lay.addWidget(self.table)
        lay.addWidget(muted_label(t("ep.causes_hint")))

    def render(self, a: Analysis):
        rows, colors = [], {}
        for i, e in enumerate(a.episodes):
            rows.append([e.time_label,
                         f"{e.bpm:.0f} BPM" if e.bpm >= 100 else t("ep.none"),
                         e.n_notes, e.loss_label, e.cause_label, e.what])
            colors[(i, 4)] = CAUSE_COLOR.get(e.cause, theme.FG_DIM)
        fill_table(self.table, rows, colors)


class TappingView(QWidget):
    """What the hands did, independently of where the cursor was."""

    TILES = (
        ("hold", "tap.hold", "tap.hold_hint"),
        ("hand_gap", "tap.hand_gap", "tap.hand_gap_hint"),
        ("alternation", "tap.alternation", "tap.alternation_hint"),
        ("single", "tap.single", "tap.single_hint"),
        ("max_bpm", "tap.max_bpm", "tap.max_bpm_hint"),
        ("fatigue", "tap.fatigue", "tap.fatigue_hint"),
        ("repeats", "tap.repeats", "tap.repeats_hint"),
    )

    def __init__(self):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        area, col = scroll_column()
        self.tiles: dict[str, StatTile] = {}
        grid_host = QWidget()
        self.cards = QGridLayout(grid_host)
        self.cards.setContentsMargins(0, 0, 0, 0)
        self.cards.setSpacing(10)
        for i, (name, caption_key, hint_key) in enumerate(self.TILES):
            tile = StatTile(t(caption_key), "—", t(hint_key))
            self.tiles[name] = tile
            self.cards.addWidget(tile, i // 2, i % 2)
        for column in (0, 1):
            self.cards.setColumnStretch(column, 1)
        col.addWidget(grid_host)

        runs_card = Card(t("tap.runs_title"), t("tap.runs_hint"))
        self.runs = make_table([t("tap.col_run"), t("tap.col_count")], 200)
        runs_card.add(self.runs)
        col.addWidget(runs_card)

        help_card = Card(t("tap.help_title"))
        help_body = rich_text(flat=True, auto_height=True)
        help_body.setHtml(f"<span class='lead'>{t('tap.help_body')}</span>")
        help_card.add(help_body)
        col.addWidget(help_card)
        col.addStretch(1)
        lay.addWidget(area, 2)

        right = QWidget()
        rcol = QVBoxLayout(right)
        rcol.setContentsMargins(0, 0, 0, 0)
        rcol.setSpacing(8)
        self.hist = pg.PlotWidget()
        theme.style_plot(self.hist, title=t("tap.hist_title"))
        self.hist.setLabel("bottom", t("tap.hist_x"), **theme.plot_label_style())
        rcol.addWidget(self.hist, 1)
        rcol.addWidget(muted_label(t("tap.hist_hint")))

        self.roll = pg.PlotWidget()
        theme.style_plot(self.roll, title=t("tap.roll_title"))
        self.roll.setLabel("left", t("tap.roll_y"), color=COL_LEFT)
        self.roll.setLabel("bottom", t("plot.timeline_x"),
                           **theme.plot_label_style())
        plot_item = self.roll.getPlotItem()
        plot_item.showAxis("right")
        plot_item.getAxis("right").setLabel(t("tap.roll_y2"), color=COL_RIGHT)
        plot_item.getAxis("right").setPen(theme.LINE)
        plot_item.getAxis("right").setTextPen(theme.PLOT_AXIS)
        plot_item.getAxis("right").enableAutoSIPrefix(False)
        self.roll_right = pg.ViewBox()
        plot_item.scene().addItem(self.roll_right)
        plot_item.getAxis("right").linkToView(self.roll_right)
        self.roll_right.setXLink(plot_item)
        plot_item.vb.sigResized.connect(self._sync_roll_axes)
        rcol.addWidget(self.roll, 1)
        rcol.addWidget(muted_label(t("tap.roll_hint")))
        lay.addWidget(right, 3)

    def _sync_roll_axes(self):
        plot_item = self.roll.getPlotItem()
        self.roll_right.setGeometry(plot_item.vb.sceneBoundingRect())
        self.roll_right.linkedViewChanged(plot_item.vb, self.roll_right.XAxis)

    def render(self, a: Analysis):
        MS = t("unit.ms")
        self.hist.clear()
        self.roll.clear()
        self.roll_right.clear()
        self.runs.setRowCount(0)

        stats = a.tapping
        if stats is None or not stats.intervals:
            for tile in self.tiles.values():
                tile.set_value("—")
            return

        fatigue_tone = ("bad" if stats.fatigue > 40 else
                        "warn" if stats.fatigue > 15 else "good")
        self.tiles["hold"].set_hint(
            t("tap.hold_hint") + " · "
            + t("tap.hold_spread", spread=stats.hold_spread))
        values = {
            "hold": (t("tap.hold_value", ms=stats.median_hold), ""),
            "hand_gap": (f"{stats.hand_hold_gap:+.0f} {MS}", ""),
            "alternation": (f"{stats.alternation * 100:.0f}%", ""),
            "single": (f"{stats.single_tap_share * 100:.0f}%", ""),
            "max_bpm": (f"{stats.max_sustained_bpm:.0f}", "accent"),
            "fatigue": (f"{stats.fatigue:+.0f} UR", fatigue_tone),
            "repeats": (f"{stats.fast_repeats}",
                        "bad" if stats.fast_repeats else "good"),
        }
        for name, (text, tone) in values.items():
            self.tiles[name].set_value(text, tone)

        centers, counts = interval_histogram(stats)
        if centers:
            self.hist.addItem(pg.PlotCurveItem(
                centers, counts, pen=pg.mkPen(COL_LEFT, width=2), fillLevel=0,
                brush=pg.mkBrush(QColor(COL_LEFT).darker(280))))

        if stats.rolling:
            xs = [r[0] / 1000.0 for r in stats.rolling]
            self.roll.addItem(pg.PlotCurveItem(
                xs, [r[1] for r in stats.rolling],
                pen=pg.mkPen(COL_LEFT, width=2)))
            self.roll_right.addItem(pg.PlotCurveItem(
                xs, [r[2] for r in stats.rolling],
                pen=pg.mkPen(COL_RIGHT, width=1, style=Qt.DashLine)))
            self._sync_roll_axes()

        fill_table(self.runs, [[length, count] for length, count
                               in sorted(stats.same_hand_runs.items())])


class AnalysisTab(QWidget):
    analysed = Signal(object)

    def __init__(self, index: BeatmapIndex, cfg: Config):
        super().__init__()
        self.index, self.cfg = index, cfg
        self.worker: AnalyseWorker | None = None
        self.analysis: Analysis | None = None
        self.device: dict | None = None
        self.last_path: str | None = None

        root = QVBoxLayout(self)
        root.setSpacing(10)
        top = QHBoxLayout()
        top.setSpacing(10)
        self.drop = DropArea()
        self.drop.dropped.connect(self.load)
        top.addWidget(self.drop, 1)

        col = QVBoxLayout()
        col.setSpacing(6)
        open_btn = QPushButton(t("analysis.open_replay"))
        open_btn.setObjectName("primary")
        open_btn.clicked.connect(self.pick)
        col.addWidget(open_btn)
        last_btn = QPushButton(t("analysis.last_replay"))
        last_btn.clicked.connect(self.load_latest)
        col.addWidget(last_btn)
        self.btn_session = QPushButton(t("analysis.attach_session"))
        self.btn_session.setToolTip(t("analysis.attach_session_tip"))
        self.btn_session.clicked.connect(self.attach_session)
        col.addWidget(self.btn_session)
        top.addLayout(col)
        root.addLayout(top)

        head = QHBoxLayout()
        head.setSpacing(10)
        self.header = QLabel(t("analysis.no_replay"))
        self.header.setObjectName("h1")
        head.addWidget(self.header)
        self.source_badge = Badge("", theme.FG_MUTED)
        self.source_badge.setVisible(False)
        head.addWidget(self.source_badge, 0, Qt.AlignVCenter)
        head.addStretch(1)
        root.addLayout(head)

        self.stats = QHBoxLayout()
        self.stats.setSpacing(10)
        root.addLayout(self.stats)

        self.views = QTabWidget()
        self.overview = OverviewView()
        self.aim = AimView()
        self.tapping = TappingView()
        self.episodes = EpisodesView()
        self.playback = PlaybackView()
        self.views.addTab(self.overview, t("view.overview"))
        self.views.addTab(self.aim, t("view.aim"))
        self.views.addTab(self.tapping, t("view.tapping"))
        self.views.addTab(self.episodes, t("view.episodes"))
        self.views.addTab(self.playback, t("view.playback"))
        root.addWidget(self.views, 1)

    def pick(self):
        start = (self.cfg.stable_replays
                 if Path(self.cfg.stable_replays).is_dir() else "")
        path, _ = QFileDialog.getOpenFileName(
            self, t("analysis.open_replay"), start, "osu! replay (*.osr)")
        if path:
            self.load(path)

    def load_latest(self):
        candidates: list[Path] = []
        dirs = [self.cfg.stable_replays]
        if self.cfg.lazer_dir:
            dirs.append(str(Path(self.cfg.lazer_dir) / "exports"))
        for folder in dirs:
            if folder and Path(folder).is_dir():
                candidates.extend(Path(folder).glob("*.osr"))
        if not candidates:
            self.header.setText(t("analysis.no_osr_found"))
            return
        self.load(str(max(candidates, key=lambda p: p.stat().st_mtime)))

    def attach_session(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("analysis.attach_session"), "", "JSON (*.json)")
        if not path:
            return
        try:
            session = Session.load(path)
        except Exception as exc:
            self.header.setText(t("analysis.session_unreadable", message=exc))
            return
        report = session.depth_report(self.cfg.trigger_um, self.cfg.release_um)
        if not report.get("keys"):
            self.header.setText(t("analysis.session_no_presses"))
            self.device = None
            return
        self.device = report
        self.btn_session.setText(
            t("analysis.attached", name=Path(path).name[:18]))
        if self.last_path:
            self.load(self.last_path)

    def load(self, path: str):
        self.last_path = path
        self.header.setText(t("analysis.analysing", name=Path(path).name))
        self.worker = AnalyseWorker(path, self.index, self.cfg, self.device)
        self.worker.done.connect(self.show_result)
        self.worker.failed.connect(
            lambda m: self.header.setText(t("analysis.error", message=m)))
        self.worker.start()

    def show_result(self, a: Analysis):
        self.analysis = a
        self.header.setText(a.title)
        self.source_badge.setText(
            "osu!lazer" if a.replay.source == "lazer" else "osu!stable")
        self.source_badge.setVisible(True)
        clear_layout(self.stats)
        if a.error_key or a.judge is None:
            self.overview.findings.setHtml(
                f"<p class='bad'>{a.error or t('analysis.no_data')}</p>")
            return

        MS = t("unit.ms")
        n_left, mean_left, ur_left = a.hand("left")
        n_right, mean_right, ur_right = a.hand("right")
        counts = a.judge.counts()
        spread = f"{a.aim.spread:.2f}" if a.aim and a.aim.hits else "—"
        spread_tone = ""
        if a.aim and a.aim.hits:
            spread_tone = ("bad" if a.aim.spread > 0.62 else
                           "warn" if a.aim.spread > 0.5 else "good")
        ur_tone = ("bad" if a.ur > 260 else "warn" if a.ur > 180 else "good")
        cards = [
            (t("stat.error"), f"{a.mean_error:+.1f} {MS}",
             t("stat.error_hint"),
             "warn" if abs(a.mean_error) >= 12 else "good"),
            (t("stat.ur"), f"{a.ur:.0f}",
             t("stat.ur_hint", fps=a.replay.frame_rate), ur_tone),
            (t("stat.left"), f"{mean_left:+.1f} {MS}",
             t("stat.hand_hint", ur=ur_left, n=n_left), ""),
            (t("stat.right"), f"{mean_right:+.1f} {MS}",
             t("stat.hand_hint", ur=ur_right, n=n_right), ""),
            (t("stat.counts"),
             f"{counts['300']}/{counts['100']}/{counts['50']}/{counts['miss']}",
             t("stat.counts_hint"), ""),
            (t("stat.aim_spread"), spread, t("stat.aim_spread_hint"),
             spread_tone),
        ]
        for title, value, hint, tone in cards:
            self.stats.addWidget(StatTile(title, value, hint, tone))

        self.overview.render(a)
        self.aim.render(a)
        self.tapping.render(a)
        self.episodes.render(a)
        self.playback.set_analysis(a)
        self.analysed.emit(a)


class RecordTab(QWidget):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.rec: SessionRecorder | None = None
        self.started_at = 0.0

        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.addWidget(dim_label(t("rec.info")))

        controls = Card(t("rec.controls_title"))
        row = QHBoxLayout()
        self.focus_only = QCheckBox(t("rec.focus_only"))
        self.focus_only.setChecked(cfg.only_when_focused)
        row.addWidget(self.focus_only)
        row.addSpacing(20)
        row.addWidget(QLabel(t("rec.hz_label")))
        self.hz = QDoubleSpinBox()
        self.hz.setRange(100, 1500)
        self.hz.setSingleStep(100)
        self.hz.setValue(cfg.analog_hz)
        self.hz.setToolTip(t("rec.hz_tip"))
        row.addWidget(self.hz)
        row.addStretch(1)
        self.btn = QPushButton(t("rec.start"))
        self.btn.setObjectName("primary")
        self.btn.clicked.connect(self.toggle)
        row.addWidget(self.btn)
        self.btn_save = QPushButton(t("rec.save"))
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save)
        row.addWidget(self.btn_save)
        holder = QWidget()
        holder.setLayout(row)
        controls.add(holder)
        self.keys_hint = muted_label("")
        controls.add(self.keys_hint)
        lay.addWidget(controls)

        self.status = QLabel(t("rec.idle"))
        self.status.setObjectName("mono")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

        self.travel_card = Card(t("rec.travel_title"), t("rec.travel_hint"))
        self.bar_grid = QGridLayout()
        self.bar_grid.setSpacing(8)
        grid_host = QWidget()
        grid_host.setLayout(self.bar_grid)
        self.travel_card.add(grid_host)
        lay.addWidget(self.travel_card)

        self.report_card = Card(t("rec.depth_title"), t("rec.depth_hint"))
        self.report = rich_text(flat=True)
        self.report.setMaximumHeight(190)
        self.report_card.add(self.report)
        self.report_card.setVisible(False)
        lay.addWidget(self.report_card)
        lay.addStretch(1)

        self.bars: list[QProgressBar] = []
        self.refresh_keys()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)

    def refresh_keys(self) -> None:
        """Rebuilds the travel meters after the bound keys change."""
        clear_layout(self.bar_grid)
        self.bars = []
        labels = self.cfg.key_labels
        self.keys_hint.setText(t("rec.keys_hint", keys=" · ".join(labels)))
        for i, name in enumerate(labels):
            self.bar_grid.addWidget(QLabel(t("rec.key", n=i + 1, name=name)),
                                    i, 0)
            bar = QProgressBar()
            bar.setRange(0, 4000)
            bar.setFormat("%v µm")
            self.bars.append(bar)
            self.bar_grid.addWidget(bar, i, 1)

    def toggle(self):
        if self.rec and self.rec.running:
            session = self.rec.stop()
            self.btn.setText(t("rec.start"))
            self.btn.setObjectName("primary")
            self.btn_save.setEnabled(bool(session.presses))
            duration = max(0.001, time.time() - self.started_at)
            self.status.setText(t(
                "rec.stopped", presses=len(session.presses),
                repeats=session.repeats_filtered, travel=len(session.travel),
                hz=len(session.travel) / duration, cursor=len(session.cursor)))
            self.show_depth(session)
            return

        self.cfg.analog_hz = self.hz.value()
        self.cfg.only_when_focused = self.focus_only.isChecked()
        self.rec = SessionRecorder(only_when_focused=self.cfg.only_when_focused,
                                   analog_hz=self.cfg.analog_hz,
                                   key_codes=self.cfg.keys)
        self.rec.session.only_when_focused = self.cfg.only_when_focused
        if not self.rec.start():
            self.status.setText(t("rec.failed", message=self.rec.error))
            return
        self.started_at = time.time()
        self.btn.setText(t("rec.stop"))
        self.btn_save.setEnabled(False)
        tail = "" if self.rec.analog_available else t("rec.no_analog")
        self.status.setText(t("rec.running", sec=0, presses=0, travel=0,
                              hz=0, cursor=0, repeats=0) + tail)

    def tick(self):
        if not (self.rec and self.rec.running):
            return
        session = self.rec.session
        duration = max(0.001, time.time() - self.started_at)
        self.status.setText(t(
            "rec.running", sec=duration, presses=len(session.presses),
            travel=len(session.travel), hz=len(session.travel) / duration,
            cursor=len(session.cursor), repeats=session.repeats_filtered))
        if session.travel:
            values = session.travel[-1][1]
            for i, bar in enumerate(self.bars):
                if i < len(values):
                    bar.setValue(int(values[i]))

    def show_depth(self, session: Session):
        report = session.depth_report(self.cfg.trigger_um, self.cfg.release_um)
        keys = report.get("keys", {})
        if not keys:
            self.report_card.setVisible(False)
            return
        html = [f"<p class='lead'>{t('rec.depth_head', trigger=report['trigger_um'] / 1000, release=report['release_um'] / 1000)}</p>",
                "<table cellpadding=4><tr>"
                f"<th>{t('rec.depth_key')}</th>"
                f"<th>{t('rec.depth_n')}</th>"
                f"<th>{t('rec.depth_median')}</th>"
                f"<th>{t('rec.depth_p10')}</th>"
                f"<th>{t('rec.depth_margin')}</th>"
                f"<th>{t('rec.depth_bottom')}</th></tr>"]
        for name, data in keys.items():
            tone = ("bad" if data["margin_p10"] < report["trigger_um"] * 0.3
                    else "good")
            html.append(
                f"<tr><td>{name}</td><td>{data['n']}</td>"
                f"<td>{data['median'] / 1000:.2f} mm</td>"
                f"<td>{data['p10'] / 1000:.2f} mm</td>"
                f"<td class='{tone}'>{data['margin_p10'] / 1000:+.2f} mm</td>"
                f"<td>{data['bottomed'] * 100:.0f}%</td></tr>")
        html.append("</table>")
        self.report.setHtml("".join(html))
        self.report_card.setVisible(True)

    def save(self):
        if not self.rec:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t("rec.save_dialog"), f"session_{int(self.started_at)}.json",
            "JSON (*.json)")
        if path:
            self.rec.session.save(path)
            self.status.setText(t("rec.saved", path=path))


class ExerciseCard(Card):
    """One drill: what is wrong, what to play, and when it is fixed."""

    practise = Signal(float)

    def __init__(self, exercise, parent=None):
        super().__init__(parent=parent)
        colour = PRIORITY_COLOR.get(exercise.priority, theme.INFO)

        head = QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(Badge(t("tr.priority", n=exercise.priority), colour))
        title = QLabel(exercise.title)
        title.setObjectName("h2")
        title.setWordWrap(True)
        head.addWidget(title, 1)
        host = QWidget()
        host.setLayout(head)
        self.add(host)

        for caption, text in ((t("tr.problem"), exercise.why),
                              (t("tr.drill"), exercise.how)):
            self.add(section_label(caption))
            body = QLabel(text)
            body.setWordWrap(True)
            body.setObjectName("dim")
            self.add(body)

        self.add(section_label(t("tr.target")))
        check = QLabel(exercise.check)
        check.setWordWrap(True)
        check.setStyleSheet(f"color: {theme.GOOD};")
        self.add(check)

        if exercise.target_bpm:
            button = QPushButton(t("tr.open_trainer", bpm=exercise.target_bpm))
            button.setObjectName("ghost")
            button.clicked.connect(
                lambda _=False, b=exercise.target_bpm: self.practise.emit(b))
            row = QHBoxLayout()
            row.addWidget(button)
            row.addStretch(1)
            host = QWidget()
            host.setLayout(row)
            self.add(host)


class TrainingTab(QWidget):
    practise = Signal(float)

    def __init__(self, index: BeatmapIndex, cfg: Config):
        super().__init__()
        self.index, self.cfg = index, cfg
        self.analysis: Analysis | None = None
        self.profiles: list = []
        self.worker: MapScanWorker | None = None

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        left = QWidget()
        lcol = QVBoxLayout(left)
        lcol.setContentsMargins(0, 0, 0, 0)
        lcol.setSpacing(10)
        self.head = QLabel(t("tr.head_title"))
        self.head.setObjectName("h1")
        lcol.addWidget(self.head)
        self.head_note = dim_label(t("tr.placeholder"))
        lcol.addWidget(self.head_note)
        self.plan_area, self.plan_col = scroll_column()
        self.plan_col.addStretch(1)
        lcol.addWidget(self.plan_area, 1)
        lay.addWidget(left, 3)

        right = QWidget()
        rcol = QVBoxLayout(right)
        rcol.setContentsMargins(0, 0, 0, 0)
        rcol.setSpacing(10)
        finder = Card(t("tr.maps_title"), t("tr.maps_hint"))
        row = QHBoxLayout()
        row.addWidget(QLabel(t("tr.target_bpm")))
        self.bpm = QDoubleSpinBox()
        self.bpm.setRange(60, 400)
        self.bpm.setValue(180)
        row.addWidget(self.bpm)
        row.addStretch(1)
        self.btn_scan = QPushButton(t("tr.scan"))
        self.btn_scan.clicked.connect(self.scan)
        row.addWidget(self.btn_scan)
        host = QWidget()
        host.setLayout(row)
        finder.add(host)
        self.bar = QProgressBar()
        self.bar.setVisible(False)
        finder.add(self.bar)
        self.maps = make_table(
            [t("tr.col_map"), t("tr.col_diff"), t("tr.col_bpm"),
             t("tr.col_notes"), t("tr.col_cs"), t("tr.col_od")])
        finder.add(self.maps, 1)
        rcol.addWidget(finder, 1)
        lay.addWidget(right, 2)

    def set_analysis(self, a: Analysis):
        self.analysis = a
        clear_layout(self.plan_col)
        if not a.plan:
            self.head_note.setText(t("tr.none"))
            self.plan_col.addStretch(1)
            return
        top = a.plan[0]
        self.head_note.setText(t("tr.head_body", first=top.title,
                                 n=len(a.plan)))
        for exercise in a.plan:
            card = ExerciseCard(exercise)
            card.practise.connect(self._practise)
            self.plan_col.addWidget(card)
        self.plan_col.addStretch(1)
        for exercise in a.plan:
            if exercise.target_bpm:
                self.bpm.setValue(exercise.target_bpm)
                break

    def _practise(self, bpm: float) -> None:
        self.bpm.setValue(bpm)
        self.practise.emit(bpm)

    def scan(self):
        paths = list(self.index.by_md5.values())
        if not paths:
            self.head_note.setText(t("tr.index_empty"))
            return
        self.btn_scan.setEnabled(False)
        self.bar.setVisible(True)
        self.worker = MapScanWorker(paths)
        self.worker.progress.connect(self.on_progress)
        self.worker.done.connect(self.on_done)
        self.worker.start()

    def on_progress(self, i, total, name):
        self.bar.setMaximum(max(total, 1))
        self.bar.setValue(i)

    def on_done(self, profiles):
        self.profiles = profiles
        self.bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        found = find_practice_maps(self.profiles, self.bpm.value())
        fill_table(self.maps,
                   [[p.title[:60], p.version[:28], f"{p.stream_bpm:.0f}",
                     p.stream_notes, f"{p.cs:.1f}", f"{p.od:.1f}"]
                    for p in found])


class SettingsTab(QWidget):
    language_changed = Signal(str)
    keys_changed = Signal()

    def __init__(self, index: BeatmapIndex, cfg: Config):
        super().__init__()
        self.index, self.cfg = index, cfg
        self.worker: IndexWorker | None = None
        area, lay = scroll_column()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(11, 11, 11, 11)
        outer.addWidget(area)

        logo = ASSETS / "logo.png"
        head = QHBoxLayout()
        head.setSpacing(14)
        if logo.exists():
            picture = QLabel()
            picture.setPixmap(QPixmap(str(logo)).scaled(
                72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            head.addWidget(picture)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        name = QLabel("osu-checker")
        name.setObjectName("h1")
        titles.addWidget(name)
        titles.addWidget(dim_label(t("app.subtitle")))
        head.addLayout(titles, 1)
        host = QWidget()
        host.setLayout(head)
        lay.addWidget(host)

        general = Card(t("set.general_title"))
        row = QHBoxLayout()
        row.addWidget(QLabel(t("set.language")), 1)
        self.language = QComboBox()
        for code, label in LANGUAGES.items():
            self.language.addItem(label, code)
        self.language.setCurrentIndex(max(0, self.language.findData(cfg.language)))
        self.language.currentIndexChanged.connect(self.on_language)
        row.addWidget(self.language, 2)
        row.addWidget(muted_label(t("set.language_hint")), 1)
        host = QWidget()
        host.setLayout(row)
        general.add(host)
        lay.addWidget(general)

        keys = Card(t("set.keys_title"), t("set.keys_hint"))
        grid = QGridLayout()
        grid.setSpacing(8)
        self.key_buttons: list[KeyCaptureButton] = []
        for i in range(NUM_KEYS):
            grid.addWidget(QLabel(t("set.key_slot", n=i + 1)), i, 0)
            button = KeyCaptureButton(self.cfg.keys[i], t("set.key_prompt"))
            button.captured.connect(
                lambda code, slot=i: self.on_key_captured(slot, code))
            self.key_buttons.append(button)
            grid.addWidget(button, i, 1)
            grid.addWidget(muted_label(t("set.key_slot_hint", n=i + 1)), i, 2)
        grid.setColumnStretch(2, 1)
        host = QWidget()
        host.setLayout(grid)
        keys.add(host)
        self.keys_status = muted_label("")
        keys.add(self.keys_status)
        lay.addWidget(keys)

        thresholds = Card(t("set.thresholds_title"), t("set.thresholds_hint"))
        row = QHBoxLayout()
        row.addWidget(QLabel(t("set.trigger")))
        self.trigger = QSpinBox()
        self.trigger.setRange(50, 3900)
        self.trigger.setSingleStep(50)
        self.trigger.setSuffix(" µm")
        self.trigger.setValue(cfg.trigger_um)
        row.addWidget(self.trigger)
        row.addSpacing(18)
        row.addWidget(QLabel(t("set.release")))
        self.release = QSpinBox()
        self.release.setRange(50, 3900)
        self.release.setSingleStep(50)
        self.release.setSuffix(" µm")
        self.release.setValue(cfg.release_um)
        row.addWidget(self.release)
        row.addStretch(1)
        host = QWidget()
        host.setLayout(row)
        thresholds.add(host)
        lay.addWidget(thresholds)

        paths = Card(t("set.paths_title"), t("set.paths_hint"))
        self.fields: dict[str, QLineEdit] = {}
        for key, label in (("stable_songs", t("set.songs")),
                           ("stable_replays", t("set.replays")),
                           ("lazer_dir", t("set.lazer"))):
            line = QHBoxLayout()
            line.addWidget(QLabel(label), 1)
            edit = QLineEdit(getattr(cfg, key))
            self.fields[key] = edit
            line.addWidget(edit, 2)
            browse = QPushButton("…")
            browse.setFixedWidth(44)
            browse.clicked.connect(lambda _=False, e=edit: self.browse(e))
            line.addWidget(browse)
            host = QWidget()
            host.setLayout(line)
            paths.add(host)

        buttons = QHBoxLayout()
        save = QPushButton(t("set.save"))
        save.setObjectName("primary")
        save.clicked.connect(self.save)
        buttons.addWidget(save)
        self.btn_index = QPushButton(t("set.rebuild"))
        self.btn_index.clicked.connect(self.rebuild)
        buttons.addWidget(self.btn_index)
        buttons.addStretch(1)
        host = QWidget()
        host.setLayout(buttons)
        paths.add(host)
        self.bar = QProgressBar()
        self.bar.setVisible(False)
        paths.add(self.bar)
        self.status = muted_label(t("set.index_count", n=len(index.by_md5)))
        paths.add(self.status)
        lay.addWidget(paths)
        lay.addStretch(1)
        self._show_keys()

    def on_language(self):
        code = self.language.currentData()
        if code and code != self.cfg.language:
            self.cfg.language = code
            self.save()
            self.language_changed.emit(code)

    def on_key_captured(self, slot: int, code: int) -> None:
        codes = list(self.cfg.keys)
        if code in codes and codes.index(code) != slot:
            self.keys_status.setText(t("set.key_taken", key=key_name(code)))
            self.key_buttons[slot].set_code(codes[slot])
            return
        codes[slot] = code
        self.cfg.key_codes = codes
        self.cfg.save()
        self._show_keys()
        self.keys_changed.emit()

    def _show_keys(self) -> None:
        self.keys_status.setText(
            t("set.keys_now", keys=" · ".join(self.cfg.key_labels)))

    def browse(self, edit: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, t("set.browse"),
                                                  edit.text())
        if folder:
            edit.setText(folder)

    def save(self):
        for key, edit in self.fields.items():
            setattr(self.cfg, key, edit.text())
        self.cfg.trigger_um = self.trigger.value()
        self.cfg.release_um = self.release.value()
        self.cfg.save()
        self.status.setText(t("set.saved"))

    def rebuild(self):
        self.save()
        self.btn_index.setEnabled(False)
        self.bar.setVisible(True)
        self.worker = IndexWorker(self.index, self.cfg.stable_songs,
                                  self.cfg.lazer_dir)
        self.worker.progress.connect(self.on_progress)
        self.worker.done.connect(self.on_done)
        self.worker.start()

    def on_progress(self, i, total, name):
        self.bar.setMaximum(max(total, 1))
        self.bar.setValue(i)
        self.status.setText(t("set.scanning", i=i, total=total, name=name))

    def on_done(self, added):
        self.bar.setVisible(False)
        self.btn_index.setEnabled(True)
        self.status.setText(t("set.done", added=added,
                              total=len(self.index.by_md5)))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(app_icon())
        self.resize(1400, 940)
        self.cfg = Config.load()
        set_language(self.cfg.language)
        self.index = BeatmapIndex()
        self.setAcceptDrops(True)
        self.build()

    def build(self, restore_path: str | None = None):
        self.setWindowTitle(t("app.title"))
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.analysis_tab = AnalysisTab(self.index, self.cfg)
        self.record_tab = RecordTab(self.cfg)
        self.trainer_tab = TrainerTab(self.cfg)
        self.training_tab = TrainingTab(self.index, self.cfg)
        settings_tab = SettingsTab(self.index, self.cfg)
        self.analysis_tab.analysed.connect(self.training_tab.set_analysis)
        self.training_tab.practise.connect(self.open_trainer)
        settings_tab.language_changed.connect(self.change_language)
        settings_tab.keys_changed.connect(self.record_tab.refresh_keys)
        settings_tab.keys_changed.connect(self.trainer_tab.refresh_keys)
        self.tabs.addTab(self.analysis_tab, t("tab.analysis"))
        self.tabs.addTab(self.record_tab, t("tab.record"))
        self.tabs.addTab(self.trainer_tab, t("tab.trainer"))
        self.tabs.addTab(self.training_tab, t("tab.training"))
        self.tabs.addTab(settings_tab, t("tab.settings"))
        self.setCentralWidget(self.tabs)
        if restore_path:
            self.analysis_tab.load(restore_path)

    def open_trainer(self, bpm: float) -> None:
        self.trainer_tab.bpm.setValue(int(round(bpm)))
        self.tabs.setCurrentWidget(self.trainer_tab)

    def change_language(self, code: str):
        previous = self.analysis_tab.last_path if self.analysis_tab else None
        set_language(code)
        self.build(restore_path=previous)

    def dragEnterEvent(self, event):
        if any(u.toLocalFile().lower().endswith(".osr")
               for u in event.mimeData().urls()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".osr"):
                self.analysis_tab.load(path)
                break


def run():
    app = QApplication([])
    app.setApplicationName("osu-checker")
    app.setWindowIcon(app_icon())
    theme.apply(app)
    pg.setConfigOption("background", theme.BG_PANEL)
    pg.setConfigOption("foreground", theme.PLOT_AXIS)
    # Antialiasing stays off. On a dense, spiky polyline -- which is exactly
    # what the trainer's interval plot is -- Qt spends about 400 ms on a
    # single redraw, against 15 ms without. That is not a slow frame, it is
    # a stalled application: the metronome falls behind, and the thread that
    # timestamps key presses is starved long enough to bunch two taps into
    # one, which then reads as an impossible tempo.
    pg.setConfigOption("antialias", False)
    window = MainWindow()
    window.show()
    app.exec()

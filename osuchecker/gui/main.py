"""Main application window."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSplitter, QTableWidget,
    QTableWidgetItem, QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

from ..analysis.episodes import (CAUSE_AIM, CAUSE_EARLY, CAUSE_LATE,
                                 CAUSE_SCATTER)
from ..analysis.pipeline import Analysis, analyse
from ..analysis.training import find_practice_maps, scan_maps
from ..config import Config
from ..i18n import LANGUAGES, set_language, t
from ..paths import resource_path
from ..recorder import Session, SessionRecorder
from ..replay.index import BeatmapIndex

ASSETS = resource_path("assets")
COL_LEFT = "#4da3ff"
COL_RIGHT = "#ff7ab6"
SEV_COLOR = {"high": "#ff5c5c", "medium": "#ffb84d", "info": "#7ec8e3"}
CAUSE_COLOR = {CAUSE_LATE: "#ff5c5c", CAUSE_EARLY: "#ffb84d",
               CAUSE_SCATTER: "#c792ea", CAUSE_AIM: "#66d9a6"}
KEYS = ("P", "V", "B")


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

    IDLE = "QFrame { border: 2px dashed #5a5a5a; border-radius: 8px; }"
    ACTIVE = "QFrame { border: 2px dashed #4da3ff; border-radius: 8px; }"

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(66)
        self.setStyleSheet(self.IDLE)
        lay = QVBoxLayout(self)
        label = QLabel(t("analysis.drop_hint"))
        label.setAlignment(Qt.AlignCenter)
        lay.addWidget(label)

    def dragEnterEvent(self, event):
        if any(u.toLocalFile().lower().endswith(".osr")
               for u in event.mimeData().urls()):
            event.acceptProposedAction()
            self.setStyleSheet(self.ACTIVE)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.IDLE)

    def dropEvent(self, event):
        self.setStyleSheet(self.IDLE)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".osr"):
                self.dropped.emit(path)
                break


def stat_box(title: str, value: str, hint: str = "") -> QGroupBox:
    box = QGroupBox(title)
    lay = QVBoxLayout(box)
    label = QLabel(value)
    font = QFont()
    font.setPointSize(15)
    font.setBold(True)
    label.setFont(font)
    lay.addWidget(label)
    if hint:
        sub = QLabel(hint)
        sub.setStyleSheet("color: #9a9a9a;")
        lay.addWidget(sub)
    return box


def make_table(headers: list[str], max_height: int | None = None) -> QTableWidget:
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    if max_height:
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


class OverviewView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        split = QSplitter(Qt.Horizontal)
        self.findings = QTextBrowser()
        split.addWidget(self.findings)

        right = QWidget()
        col = QVBoxLayout(right)
        self.hist = pg.PlotWidget(title=t("plot.hist_title"))
        self.hist.addLegend()
        self.hist.setLabel("bottom", t("plot.hist_x"))
        col.addWidget(self.hist, 1)
        self.timeline = pg.PlotWidget(title=t("plot.timeline_title"))
        self.timeline.setLabel("bottom", t("plot.timeline_x"))
        self.timeline.setLabel("left", t("plot.timeline_y"))
        col.addWidget(self.timeline, 1)
        self.table = make_table(
            [t("col.bpm"), t("col.notes"), t("col.error"), t("col.ur"),
             t("col.drift"), t("col.misses"), t("col.extras")], 180)
        col.addWidget(self.table)
        split.addWidget(right)
        split.setSizes([430, 760])
        lay.addWidget(split)

    def render(self, a: Analysis):
        self.findings.clear()
        self.hist.clear()
        self.timeline.clear()
        self.table.setRowCount(0)
        if a.judge is None:
            return

        html = []
        for f in a.findings:
            color = SEV_COLOR.get(f.severity, "#cccccc")
            block = (f"<div style='margin-bottom:14px'>"
                     f"<span style='color:{color};font-weight:bold'>"
                     f"[{f.severity_label} · {f.area_label}]</span><br>"
                     f"<b>{f.title}</b><br>{f.detail}")
            if f.action:
                block += f"<br><i style='color:#8fd18f'>→ {f.action}</i>"
            html.append(block + "</div>")
        self.findings.setHtml("".join(html))

        limit = max(20.0, a.judge.windows["50"])
        for key, color, name in (("left", COL_LEFT, t("hand.left")),
                                 ("right", COL_RIGHT, t("hand.right"))):
            errors = a.judge.errors(key)
            if len(errors) < 5:
                continue
            counts, edges = np.histogram(np.clip(errors, -limit, limit),
                                         bins=48, range=(-limit, limit))
            centers = (edges[:-1] + edges[1:]) / 2
            self.hist.addItem(pg.PlotCurveItem(
                centers, counts, pen=pg.mkPen(color, width=2), name=name,
                fillLevel=0, brush=pg.mkBrush(QColor(color).darker(220))))
        for window, color in (("300", "#66d9a6"), ("100", "#e3c76a")):
            for sign in (-1, 1):
                self.hist.addItem(pg.InfiniteLine(
                    pos=sign * a.judge.windows[window], angle=90,
                    pen=pg.mkPen(color, style=Qt.DashLine)))

        for key, color in (("left", COL_LEFT), ("right", COL_RIGHT)):
            points = [(j.press_time / 1000.0, j.error)
                      for j in a.judge.judgements
                      if j.error is not None and j.key == key]
            if points:
                xs, ys = zip(*points)
                self.timeline.addItem(pg.ScatterPlotItem(
                    xs, ys, size=3, pen=None, brush=pg.mkBrush(color)))
        self.timeline.addItem(pg.InfiniteLine(pos=0, angle=0,
                                              pen=pg.mkPen("#777777")))

        rows, colors = [], {}
        for r, b in enumerate([x for x in a.buckets if x.n_notes >= 20]):
            rows.append([f"{b.bpm:.0f}", b.n_notes, f"{b.mean_error:+.1f}",
                         f"{b.ur:.0f}", f"{b.mean_drift:+.1f}",
                         f"{b.miss_rate * 100:.1f}%",
                         f"{b.extra_rate * 100:.1f}%"])
            if b.mean_drift >= 8:
                colors[(r, 4)] = SEV_COLOR["high"]
            if b.extra_rate >= 0.02:
                colors[(r, 6)] = SEV_COLOR["medium"]
        fill_table(self.table, rows, colors)


class AimView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QHBoxLayout(self)
        self.plot = pg.PlotWidget(title=t("aim.plot_title"))
        self.plot.setAspectLocked(True)
        self.plot.setLabel("bottom", t("aim.axis_px"))
        lay.addWidget(self.plot, 3)

        side = QWidget()
        col = QVBoxLayout(side)
        self.summary = QTextBrowser()
        self.summary.setMaximumHeight(210)
        col.addWidget(self.summary)
        col.addWidget(QLabel(t("aim.by_jump")))
        self.by_jump = make_table(
            [t("aim.col_jump"), t("aim.col_notes"), t("aim.col_spread"),
             t("aim.col_edge"), t("aim.col_over"), t("aim.col_over_pct")])
        col.addWidget(self.by_jump)
        col.addWidget(QLabel(t("aim.by_dir")))
        self.by_dir = make_table(
            [t("aim.col_dir"), t("aim.col_notes"), t("aim.col_spread"),
             t("aim.col_over")], 200)
        col.addWidget(self.by_dir)
        lay.addWidget(side, 2)

    def render(self, a: Analysis):
        self.plot.clear()
        self.summary.clear()
        aim = a.aim
        if not aim or not aim.hits:
            self.summary.setHtml(f"<p>{t('aim.no_data')}</p>")
            return

        radius = aim.radius
        for value, color, dash in ((radius, "#4da3ff", Qt.SolidLine),
                                   (radius * 0.75, "#5a5a5a", Qt.DashLine)):
            angles = np.linspace(0, 2 * np.pi, 180)
            self.plot.addItem(pg.PlotCurveItem(
                value * np.cos(angles), value * np.sin(angles),
                pen=pg.mkPen(color, width=2, style=dash)))
        self.plot.addItem(pg.ScatterPlotItem(
            [h.dx for h in aim.hits], [-h.dy for h in aim.hits],
            size=4, pen=None, brush=pg.mkBrush(255, 122, 182, 110)))
        bias_x, bias_y = aim.bias
        self.plot.addItem(pg.ScatterPlotItem(
            [bias_x], [-bias_y], size=16, symbol="+",
            pen=pg.mkPen("#ffe066", width=3)))

        self.summary.setHtml(
            f"<p><b>{t('aim.radius')}:</b> {radius:.1f} px</p>"
            f"<p><b>{t('aim.bias')}:</b> x {bias_x:+.1f} px, "
            f"y {bias_y:+.1f} px<br>"
            f"<span style='color:#9a9a9a'>{t('aim.bias_hint')}</span></p>"
            f"<p><b>{t('aim.spread')}:</b> "
            f"{t('aim.spread_value', value=aim.spread)}<br>"
            f"<b>{t('aim.edge')}:</b> {aim.edge_rate * 100:.1f}%<br>"
            f"<b>{t('aim.overshoot')}:</b> "
            f"{t('aim.overshoot_value', px=aim.mean_overshoot, pct=aim.overshoot_rate * 100)}"
            f"</p>")

        rows, colors = [], {}
        for i, b in enumerate(aim.by_jump_size()):
            high = "∞" if b["hi"] > 1e8 else f"{b['hi']:.0f}"
            rows.append([f"{b['lo']:.0f}–{high}", b["n"], f"{b['spread']:.2f}",
                         f"{b['edge_rate'] * 100:.1f}%", f"{b['overshoot']:.1f}",
                         f"{b['overshoot_rate'] * 100:.0f}%"])
            if b["edge_rate"] > 0.12:
                colors[(i, 3)] = SEV_COLOR["high"]
            if b["overshoot_rate"] > 0.30:
                colors[(i, 5)] = SEV_COLOR["medium"]
        fill_table(self.by_jump, rows, colors)
        fill_table(self.by_dir,
                   [[d["name"], d["n"], f"{d['spread']:.2f}",
                     f"{d['overshoot']:.1f}"] for d in aim.by_direction()])


class EpisodesView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        head = QLabel(t("ep.head"))
        head.setWordWrap(True)
        head.setStyleSheet("color:#9a9a9a")
        lay.addWidget(head)
        self.table = make_table(
            [t("ep.col_time"), t("ep.col_tempo"), t("ep.col_notes"),
             t("ep.col_loss"), t("ep.col_cause"), t("ep.col_what")])
        header = self.table.horizontalHeader()
        for c in range(5):
            header.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        lay.addWidget(self.table)

    def render(self, a: Analysis):
        rows, colors = [], {}
        for i, e in enumerate(a.episodes):
            rows.append([e.time_label,
                         f"{e.bpm:.0f} BPM" if e.bpm >= 100 else t("ep.none"),
                         e.n_notes, e.loss_label, e.cause_label, e.what])
            colors[(i, 4)] = CAUSE_COLOR.get(e.cause, "#cccccc")
        fill_table(self.table, rows, colors)


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
        top = QHBoxLayout()
        self.drop = DropArea()
        self.drop.dropped.connect(self.load)
        top.addWidget(self.drop, 1)

        col = QVBoxLayout()
        open_btn = QPushButton(t("analysis.open_replay"))
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

        self.header = QLabel(t("analysis.no_replay"))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.header.setFont(font)
        root.addWidget(self.header)

        self.stats = QHBoxLayout()
        root.addLayout(self.stats)

        self.views = QTabWidget()
        self.overview = OverviewView()
        self.aim = AimView()
        self.episodes = EpisodesView()
        self.views.addTab(self.overview, t("view.overview"))
        self.views.addTab(self.aim, t("view.aim"))
        self.views.addTab(self.episodes, t("view.episodes"))
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
        source = "osu!lazer" if a.replay.source == "lazer" else "osu!stable"
        self.header.setText(f"{a.title}    ·    {source}")
        while self.stats.count():
            item = self.stats.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if a.error_key or a.judge is None:
            self.overview.findings.setHtml(
                f"<p style='color:#ff8a8a'>"
                f"{a.error or t('analysis.no_data')}</p>")
            return

        n_left, mean_left, ur_left = a.hand("left")
        n_right, mean_right, ur_right = a.hand("right")
        counts = a.judge.counts()
        spread = f"{a.aim.spread:.2f}" if a.aim and a.aim.hits else "—"
        cards = [
            (t("stat.error"), f"{a.mean_error:+.1f} ms", t("stat.error_hint")),
            (t("stat.ur"), f"{a.ur:.0f}",
             t("stat.ur_hint", fps=a.replay.frame_rate)),
            (t("stat.left"), f"{mean_left:+.1f} ms",
             t("stat.hand_hint", ur=ur_left, n=n_left)),
            (t("stat.right"), f"{mean_right:+.1f} ms",
             t("stat.hand_hint", ur=ur_right, n=n_right)),
            (t("stat.counts"),
             f"{counts['300']}/{counts['100']}/{counts['50']}/{counts['miss']}",
             t("stat.counts_hint")),
            (t("stat.aim_spread"), spread, t("stat.aim_spread_hint")),
        ]
        for title, value, hint in cards:
            self.stats.addWidget(stat_box(title, value, hint))

        self.overview.render(a)
        self.aim.render(a)
        self.episodes.render(a)
        self.analysed.emit(a)


class RecordTab(QWidget):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.rec: SessionRecorder | None = None
        self.started_at = 0.0

        lay = QVBoxLayout(self)
        info = QLabel(t("rec.info"))
        info.setWordWrap(True)
        info.setStyleSheet("color:#9a9a9a")
        lay.addWidget(info)

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
        lay.addLayout(row)

        buttons = QHBoxLayout()
        self.btn = QPushButton(t("rec.start"))
        self.btn.clicked.connect(self.toggle)
        buttons.addWidget(self.btn)
        self.btn_save = QPushButton(t("rec.save"))
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save)
        buttons.addWidget(self.btn_save)
        buttons.addStretch(1)
        lay.addLayout(buttons)

        self.status = QLabel(t("rec.idle"))
        lay.addWidget(self.status)

        self.report = QTextBrowser()
        self.report.setMaximumHeight(190)
        self.report.setVisible(False)
        lay.addWidget(self.report)

        grid = QGridLayout()
        lay.addLayout(grid)
        self.bars: dict[str, QProgressBar] = {}
        for i, name in enumerate(KEYS):
            grid.addWidget(QLabel(t("rec.key", name=name)), i, 0)
            bar = QProgressBar()
            bar.setRange(0, 4000)
            bar.setFormat("%v µm")
            self.bars[name] = bar
            grid.addWidget(bar, i, 1)
        lay.addStretch(1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)

    def toggle(self):
        if self.rec and self.rec.running:
            session = self.rec.stop()
            self.btn.setText(t("rec.start"))
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
                                   analog_hz=self.cfg.analog_hz)
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
            for i, name in enumerate(KEYS):
                if i < len(values):
                    self.bars[name].setValue(int(values[i]))

    def show_depth(self, session: Session):
        report = session.depth_report(self.cfg.trigger_um, self.cfg.release_um)
        keys = report.get("keys", {})
        if not keys:
            self.report.setVisible(False)
            return
        html = [f"<p>{t('rec.depth_head', trigger=report['trigger_um'] / 1000, release=report['release_um'] / 1000)}</p>",
                "<table cellpadding=4><tr>"
                f"<td><b>{t('rec.depth_key')}</b></td>"
                f"<td><b>{t('rec.depth_n')}</b></td>"
                f"<td><b>{t('rec.depth_median')}</b></td>"
                f"<td><b>{t('rec.depth_p10')}</b></td>"
                f"<td><b>{t('rec.depth_margin')}</b></td>"
                f"<td><b>{t('rec.depth_bottom')}</b></td></tr>"]
        for name, data in keys.items():
            color = ("#ff5c5c" if data["margin_p10"] < report["trigger_um"] * 0.3
                     else "#8fd18f")
            html.append(
                f"<tr><td>{name}</td><td>{data['n']}</td>"
                f"<td>{data['median'] / 1000:.2f} mm</td>"
                f"<td>{data['p10'] / 1000:.2f} mm</td>"
                f"<td style='color:{color}'>{data['margin_p10'] / 1000:+.2f} mm</td>"
                f"<td>{data['bottomed'] * 100:.0f}%</td></tr>")
        html.append("</table>")
        self.report.setHtml("".join(html))
        self.report.setVisible(True)

    def save(self):
        if not self.rec:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t("rec.save_dialog"), f"session_{int(self.started_at)}.json",
            "JSON (*.json)")
        if path:
            self.rec.session.save(path)
            self.status.setText(t("rec.saved", path=path))


class TrainingTab(QWidget):
    def __init__(self, index: BeatmapIndex, cfg: Config):
        super().__init__()
        self.index, self.cfg = index, cfg
        self.analysis: Analysis | None = None
        self.profiles: list = []
        self.worker: MapScanWorker | None = None

        lay = QVBoxLayout(self)
        self.plan = QTextBrowser()
        lay.addWidget(self.plan, 3)

        row = QHBoxLayout()
        self.btn_scan = QPushButton(t("tr.scan"))
        self.btn_scan.clicked.connect(self.scan)
        row.addWidget(self.btn_scan)
        row.addWidget(QLabel(t("tr.target_bpm")))
        self.bpm = QDoubleSpinBox()
        self.bpm.setRange(60, 400)
        self.bpm.setValue(180)
        row.addWidget(self.bpm)
        row.addStretch(1)
        lay.addLayout(row)

        self.bar = QProgressBar()
        self.bar.setVisible(False)
        lay.addWidget(self.bar)
        self.maps = make_table(
            [t("tr.col_map"), t("tr.col_diff"), t("tr.col_bpm"),
             t("tr.col_notes"), t("tr.col_cs"), t("tr.col_od")])
        lay.addWidget(self.maps, 2)
        self.plan.setHtml(f"<p style='color:#9a9a9a'>{t('tr.placeholder')}</p>")

    def set_analysis(self, a: Analysis):
        self.analysis = a
        if not a.plan:
            self.plan.setHtml(f"<p>{t('tr.none')}</p>")
            return
        html = []
        for exercise in a.plan:
            color = {1: "#ff5c5c", 2: "#ffb84d"}.get(exercise.priority, "#7ec8e3")
            html.append(
                f"<div style='margin-bottom:18px'>"
                f"<span style='color:{color};font-weight:bold'>"
                f"{t('tr.priority', n=exercise.priority)}</span> &nbsp; "
                f"<b>{exercise.title}</b><br>"
                f"<span style='color:#9a9a9a'>{t('tr.why')}</span> "
                f"{exercise.why}<br>"
                f"<span style='color:#9a9a9a'>{t('tr.how')}</span> "
                f"{exercise.how}<br>"
                f"<i style='color:#8fd18f'>{t('tr.check')} "
                f"{exercise.check}</i></div>")
        self.plan.setHtml("".join(html))
        for exercise in a.plan:
            if exercise.target_bpm:
                self.bpm.setValue(exercise.target_bpm)
                break

    def scan(self):
        paths = list(self.index.by_md5.values())
        if not paths:
            self.plan.append(f"<p style='color:#ff8a8a'>"
                             f"{t('tr.index_empty')}</p>")
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

    def __init__(self, index: BeatmapIndex, cfg: Config):
        super().__init__()
        self.index, self.cfg = index, cfg
        self.worker: IndexWorker | None = None
        lay = QVBoxLayout(self)

        logo = ASSETS / "logo.png"
        if logo.exists():
            head = QHBoxLayout()
            picture = QLabel()
            picture.setPixmap(QPixmap(str(logo)).scaled(
                84, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            head.addWidget(picture)
            head.addWidget(QLabel(f"<h2>osu-checker</h2>"
                                  f"<span style='color:#9a9a9a'>"
                                  f"{t('app.subtitle')}</span>"), 1)
            lay.addLayout(head)

        row = QHBoxLayout()
        row.addWidget(QLabel(t("set.language")), 1)
        self.language = QComboBox()
        for code, name in LANGUAGES.items():
            self.language.addItem(name, code)
        index_of = self.language.findData(cfg.language)
        self.language.setCurrentIndex(max(0, index_of))
        self.language.currentIndexChanged.connect(self.on_language)
        row.addWidget(self.language, 2)
        hint = QLabel(t("set.language_hint"))
        hint.setStyleSheet("color:#9a9a9a")
        row.addWidget(hint)
        lay.addLayout(row)

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
            browse.setMaximumWidth(34)
            browse.clicked.connect(lambda _=False, e=edit: self.browse(e))
            line.addWidget(browse)
            lay.addLayout(line)

        buttons = QHBoxLayout()
        save = QPushButton(t("set.save"))
        save.clicked.connect(self.save)
        buttons.addWidget(save)
        self.btn_index = QPushButton(t("set.rebuild"))
        self.btn_index.clicked.connect(self.rebuild)
        buttons.addWidget(self.btn_index)
        buttons.addStretch(1)
        lay.addLayout(buttons)

        self.bar = QProgressBar()
        self.bar.setVisible(False)
        lay.addWidget(self.bar)
        self.status = QLabel(t("set.index_count", n=len(index.by_md5)))
        lay.addWidget(self.status)
        lay.addStretch(1)

    def on_language(self):
        code = self.language.currentData()
        if code and code != self.cfg.language:
            self.cfg.language = code
            self.save()
            self.language_changed.emit(code)

    def browse(self, edit: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, t("set.browse"),
                                                  edit.text())
        if folder:
            edit.setText(folder)

    def save(self):
        for key, edit in self.fields.items():
            setattr(self.cfg, key, edit.text())
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
        self.resize(1340, 900)
        self.cfg = Config.load()
        set_language(self.cfg.language)
        self.index = BeatmapIndex()
        self.setAcceptDrops(True)
        self.build()

    def build(self, restore_path: str | None = None):
        self.setWindowTitle(t("app.title"))
        tabs = QTabWidget()
        self.analysis_tab = AnalysisTab(self.index, self.cfg)
        self.training_tab = TrainingTab(self.index, self.cfg)
        settings_tab = SettingsTab(self.index, self.cfg)
        self.analysis_tab.analysed.connect(self.training_tab.set_analysis)
        settings_tab.language_changed.connect(self.change_language)
        tabs.addTab(self.analysis_tab, t("tab.analysis"))
        tabs.addTab(RecordTab(self.cfg), t("tab.record"))
        tabs.addTab(self.training_tab, t("tab.training"))
        tabs.addTab(settings_tab, t("tab.settings"))
        self.setCentralWidget(tabs)
        if restore_path:
            self.analysis_tab.load(restore_path)

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
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#232323"))
    palette.setColor(QPalette.WindowText, QColor("#e6e6e6"))
    palette.setColor(QPalette.Base, QColor("#1b1b1b"))
    palette.setColor(QPalette.AlternateBase, QColor("#262626"))
    palette.setColor(QPalette.Text, QColor("#e6e6e6"))
    palette.setColor(QPalette.Button, QColor("#2e2e2e"))
    palette.setColor(QPalette.ButtonText, QColor("#e6e6e6"))
    palette.setColor(QPalette.Highlight, QColor("#4da3ff"))
    palette.setColor(QPalette.HighlightedText, QColor("#101010"))
    app.setPalette(palette)
    pg.setConfigOption("background", "#1b1b1b")
    pg.setConfigOption("foreground", "#c8c8c8")
    window = MainWindow()
    window.show()
    app.exec()

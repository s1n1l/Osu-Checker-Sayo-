"""Headless check that every view builds and fills in all languages."""
import glob
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from osuchecker.gui import theme
from osuchecker.gui.main import MainWindow
from osuchecker.i18n import LANGUAGES, set_language

app = QApplication([])
app.setQuitOnLastWindowClosed(False)
theme.apply(app)
replay = sorted(glob.glob("S:/osu/Replays/*.osr"), key=os.path.getmtime)[-1]
results = {}
langs = list(LANGUAGES)
state = {"i": 0, "window": None}


def next_lang():
    if state["i"] >= len(langs):
        for code, info in results.items():
            print(f"[{code}] {info}")
        app.quit()
        return
    code = langs[state["i"]]
    state["i"] += 1
    set_language(code)
    w = MainWindow()
    w.cfg.language = code
    state["window"] = w
    w.show()
    tab = w.analysis_tab

    def done(a):
        pb = tab.playback
        pb.seek(pb.duration * 0.4)
        results[code] = (
            f"tabs={w.centralWidget().count()} views={tab.views.count()} "
            f"cards={tab.stats.count()} bpm={tab.overview.table.rowCount()} "
            f"aimcols={tab.aim.by_jump.columnCount()} "
            f"tapcards={tab.tapping.cards.count()} "
            f"runs={tab.tapping.runs.rowCount()} "
            f"ep={tab.episodes.table.rowCount()} "
            f"pbjumps={pb.jump.count()} pbdur={pb.duration:.0f} "
            f"readout={len(pb.readout.text())}")
        w.close()
        QTimer.singleShot(50, next_lang)

    tab.load(replay)
    tab.worker.done.connect(done)


QTimer.singleShot(0, next_lang)
QTimer.singleShot(120000, lambda: (print("TIMEOUT"), app.quit()))
app.exec()
sys.exit(0 if len(results) == len(langs) else 1)

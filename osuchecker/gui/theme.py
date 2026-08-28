"""Palette, fonts and stylesheet.

Three type roles. Body text is the system UI face. Figures inside tables
are monospaced so columns line up and a value does not jump sideways as it
changes during recording. Large readouts use a condensed display face,
which only ever shows digits and Latin units, so nothing is lost in the
Ukrainian or Chinese builds.

Colour is meaning, not decoration: green reads as fine, amber as worth a
look, red as the thing to fix. The two hands keep the same blue and pink
everywhere, plots included.
"""
from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette

UI_FONTS = ("Segoe UI Variable Text", "Segoe UI", "Inter", "Noto Sans",
            "DejaVu Sans")
MONO_FONTS = ("Cascadia Mono", "Consolas", "JetBrains Mono", "Courier New")
NUM_FONTS = ("Bahnschrift", "Segoe UI Variable Display", "Inter",
             "Cascadia Mono", "Consolas")

# Surfaces, darkest first.
BG = "#0d0f13"
BG_PANEL = "#14171d"
BG_RAISED = "#1b1f27"
BG_INPUT = "#0a0c0f"
BG_HOVER = "#232833"

LINE = "#252a34"
LINE_SOFT = "#1a1e26"

FG = "#e7eaf0"
FG_DIM = "#8d95a3"
FG_MUTED = "#5f6875"

ACCENT = "#5b8cff"
ACCENT_DIM = "#2b3f74"
ACCENT_SOFT = "#18213a"

GOOD = "#3ddc97"
WARN = "#ffb454"
BAD = "#ff5f6d"
INFO = "#67d8ef"

HAND_LEFT = "#4da3ff"
HAND_RIGHT = "#ff7ab6"

PLOT_AXIS = "#6f7784"
PLOT_GRID = "#1c212a"

SEVERITY = {"high": BAD, "medium": WARN, "info": INFO}


def _pick(candidates: tuple[str, ...], fallback: str) -> str:
    available = set(QFontDatabase.families())
    for name in candidates:
        if name in available:
            return name
    return fallback


def ui_family() -> str:
    return _pick(UI_FONTS, "Arial")


def mono_family() -> str:
    return _pick(MONO_FONTS, "Courier New")


def num_family() -> str:
    return _pick(NUM_FONTS, mono_family())


def plot_label_style() -> dict:
    return {"color": PLOT_AXIS, "font-size": "9pt"}


def style_plot(widget, *, grid: bool = True, title: str = "") -> None:
    """Gives a pyqtgraph widget the same restraint as the rest of the app."""
    item = widget.getPlotItem()
    if title:
        item.setTitle(title, color=FG_DIM, size="10pt")
    item.getViewBox().setBackgroundColor(BG_PANEL)
    if grid:
        item.showGrid(x=True, y=True, alpha=0.12)
    for name in ("left", "bottom"):
        axis = item.getAxis(name)
        axis.setPen(LINE)
        axis.setTextPen(PLOT_AXIS)
        axis.enableAutoSIPrefix(False)
    for name in ("top", "right"):
        item.showAxis(name, False)


def stylesheet() -> str:
    ui = ui_family()
    mono = mono_family()
    num = num_family()
    return f"""
    * {{
        font-family: "{ui}";
        font-size: 10pt;
    }}
    QWidget {{
        color: {FG};
        background: {BG};
    }}
    QLabel, QCheckBox, QRadioButton {{
        background: transparent;
    }}
    QToolTip {{
        color: {FG};
        background: {BG_RAISED};
        border: 1px solid {LINE};
        border-radius: 6px;
        padding: 6px 8px;
    }}

    QLabel#mono, QLabel[role="mono"] {{
        font-family: "{mono}";
        font-size: 10pt;
    }}
    QLabel#h1 {{
        font-size: 17pt;
        font-weight: 600;
        letter-spacing: -0.3px;
    }}
    QLabel#h2 {{
        font-size: 12pt;
        font-weight: 600;
    }}
    QLabel#section {{
        font-size: 9pt;
        font-weight: 600;
        color: {FG_DIM};
        letter-spacing: 1.1px;
    }}
    QLabel#dim {{
        color: {FG_DIM};
    }}
    QLabel#muted {{
        color: {FG_MUTED};
        font-size: 9pt;
    }}
    QLabel#value {{
        font-family: "{num}";
        font-size: 19pt;
        font-weight: 600;
    }}
    QLabel#huge {{
        font-family: "{num}";
        font-size: 34pt;
        font-weight: 600;
    }}

    QTabWidget::pane {{
        border: none;
        top: 4px;
    }}
    QTabBar {{
        qproperty-drawBase: 0;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {FG_DIM};
        padding: 8px 18px;
        margin-right: 4px;
        border: 1px solid transparent;
        border-radius: 9px;
    }}
    QTabBar::tab:selected {{
        color: {FG};
        background: {BG_RAISED};
        border-color: {LINE};
    }}
    QTabBar::tab:hover:!selected {{
        color: {FG};
        background: {BG_PANEL};
    }}

    QGroupBox {{
        background: {BG_PANEL};
        border: 1px solid {LINE_SOFT};
        border-radius: 10px;
        margin-top: 10px;
        padding: 12px 14px 14px 14px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 13px;
        padding: 0 5px;
        color: {FG_DIM};
        font-size: 9pt;
        font-weight: 600;
    }}

    QFrame#card {{
        background: {BG_PANEL};
        border: 1px solid {LINE_SOFT};
        border-radius: 10px;
    }}
    QFrame#tile {{
        background: {BG_PANEL};
        border: 1px solid {LINE_SOFT};
        border-radius: 10px;
    }}
    QFrame#tile:hover {{
        border-color: {LINE};
    }}
    QFrame#banner {{
        background: {ACCENT_SOFT};
        border: 1px solid {ACCENT_DIM};
        border-radius: 9px;
    }}
    QFrame#bannerWarn {{
        background: #2a2013;
        border: 1px solid #6b5121;
        border-radius: 9px;
    }}
    QPushButton {{
        background: {BG_RAISED};
        border: 1px solid {LINE};
        border-radius: 8px;
        padding: 7px 15px;
        color: {FG};
    }}
    QPushButton:hover {{
        background: {BG_HOVER};
        border-color: {ACCENT_DIM};
    }}
    QPushButton:pressed {{
        background: {BG_INPUT};
    }}
    QPushButton:disabled {{
        color: {FG_MUTED};
        background: {BG_PANEL};
        border-color: {LINE_SOFT};
    }}
    QPushButton#primary {{
        background: {ACCENT};
        border-color: {ACCENT};
        color: #0b1020;
        font-weight: 600;
    }}
    QPushButton#primary:hover {{
        background: #7aa2ff;
        border-color: #7aa2ff;
    }}
    QPushButton#primary:pressed {{
        background: {ACCENT_DIM};
        color: {FG};
    }}
    QPushButton#ghost {{
        background: transparent;
        border-color: {LINE};
        color: {FG_DIM};
    }}
    QPushButton#ghost:hover {{
        color: {FG};
        background: {BG_PANEL};
    }}
    QPushButton#capture:checked {{
        background: {ACCENT_SOFT};
        border-color: {ACCENT};
        color: {FG};
    }}

    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {{
        background: {BG_INPUT};
        border: 1px solid {LINE};
        border-radius: 8px;
        padding: 6px 9px;
        selection-background-color: {ACCENT_DIM};
    }}
    QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
        border-color: {ACCENT_DIM};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background: {BG_RAISED};
        border: 1px solid {LINE};
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {ACCENT_DIM};
        outline: none;
    }}

    QTableWidget {{
        background: {BG_INPUT};
        alternate-background-color: {BG_PANEL};
        gridline-color: {LINE_SOFT};
        border: 1px solid {LINE_SOFT};
        border-radius: 9px;
        font-family: "{mono}";
        selection-background-color: {ACCENT_SOFT};
        selection-color: {FG};
    }}
    QHeaderView::section {{
        background: {BG_PANEL};
        color: {FG_DIM};
        border: none;
        border-bottom: 1px solid {LINE};
        padding: 7px 6px;
        font-family: "{ui}";
        font-size: 9pt;
        font-weight: 600;
    }}

    QTextBrowser {{
        background: {BG_PANEL};
        border: 1px solid {LINE_SOFT};
        border-radius: 10px;
        padding: 10px 12px;
    }}
    QTextBrowser#flat {{
        background: transparent;
        border: none;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}

    QProgressBar {{
        background: {BG_INPUT};
        border: 1px solid {LINE_SOFT};
        border-radius: 7px;
        text-align: center;
        font-family: "{mono}";
        height: 16px;
    }}
    QProgressBar::chunk {{
        background: {ACCENT};
        border-radius: 6px;
    }}

    QSlider::groove:horizontal {{
        height: 4px;
        background: {LINE};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {ACCENT};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {FG};
        width: 12px;
        margin: -5px 0;
        border-radius: 6px;
    }}

    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {LINE};
        border-radius: 5px;
        background: {BG_INPUT};
    }}
    QCheckBox::indicator:hover {{
        border-color: {ACCENT_DIM};
    }}
    QCheckBox::indicator:checked {{
        background: {ACCENT};
        border-color: {ACCENT};
    }}

    QScrollBar:vertical, QScrollBar:horizontal {{
        background: transparent;
        width: 10px;
        height: 10px;
        margin: 0;
    }}
    QScrollBar::handle {{
        background: {LINE};
        border-radius: 5px;
        min-height: 28px;
        min-width: 28px;
    }}
    QScrollBar::handle:hover {{
        background: #333a46;
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        height: 0;
        width: 0;
    }}
    QScrollBar::add-page, QScrollBar::sub-page {{
        background: transparent;
    }}

    QSplitter::handle {{
        background: transparent;
    }}
    """


def palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor(BG))
    p.setColor(QPalette.WindowText, QColor(FG))
    p.setColor(QPalette.Base, QColor(BG_INPUT))
    p.setColor(QPalette.AlternateBase, QColor(BG_PANEL))
    p.setColor(QPalette.Text, QColor(FG))
    p.setColor(QPalette.Button, QColor(BG_RAISED))
    p.setColor(QPalette.ButtonText, QColor(FG))
    p.setColor(QPalette.Highlight, QColor(ACCENT))
    p.setColor(QPalette.HighlightedText, QColor("#0b1020"))
    p.setColor(QPalette.ToolTipBase, QColor(BG_RAISED))
    p.setColor(QPalette.ToolTipText, QColor(FG))
    p.setColor(QPalette.PlaceholderText, QColor(FG_MUTED))
    return p


def apply(app) -> None:
    app.setStyle("Fusion")
    app.setPalette(palette())
    font = QFont(ui_family(), 10)
    font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(font)
    app.setStyleSheet(stylesheet())

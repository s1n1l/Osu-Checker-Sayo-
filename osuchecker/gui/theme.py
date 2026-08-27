"""Palette, fonts and stylesheet.

Numbers live in a monospaced face so that columns of figures line up and a
value does not jump sideways as it changes during recording.
"""
from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette

UI_FONTS = ("Segoe UI", "Inter", "Noto Sans", "DejaVu Sans")
MONO_FONTS = ("Cascadia Mono", "Consolas", "JetBrains Mono", "Courier New")

BG = "#1a1c20"
BG_RAISED = "#22252b"
BG_INPUT = "#15171a"
FG = "#e8eaed"
FG_DIM = "#9aa0a6"
LINE = "#31353c"
ACCENT = "#4da3ff"
ACCENT_DIM = "#2b5f96"


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


def mono_font(size: int = 10, bold: bool = False) -> QFont:
    font = QFont(mono_family(), size)
    font.setBold(bold)
    font.setStyleHint(QFont.Monospace)
    return font


def stylesheet() -> str:
    ui = ui_family()
    mono = mono_family()
    return f"""
    * {{
        font-family: "{ui}";
        font-size: 10pt;
    }}
    QWidget {{
        color: {FG};
        background: {BG};
    }}
    QLabel#mono, QLabel[role="mono"] {{
        font-family: "{mono}";
        font-size: 10pt;
    }}
    QLabel#h1 {{
        font-size: 15pt;
        font-weight: 600;
    }}
    QLabel#h2 {{
        font-size: 12pt;
        font-weight: 600;
    }}
    QLabel#dim {{
        color: {FG_DIM};
    }}
    QLabel#value {{
        font-family: "{mono}";
        font-size: 16pt;
        font-weight: 600;
    }}
    QLabel#huge {{
        font-family: "{mono}";
        font-size: 34pt;
        font-weight: 600;
    }}

    QTabWidget::pane {{
        border: 1px solid {LINE};
        border-radius: 6px;
        top: -1px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {FG_DIM};
        padding: 7px 16px;
        margin-right: 2px;
        border: 1px solid transparent;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{
        color: {FG};
        background: {BG_RAISED};
        border-color: {LINE};
        border-bottom-color: {BG_RAISED};
    }}
    QTabBar::tab:hover:!selected {{
        color: {FG};
    }}

    QGroupBox {{
        background: {BG_RAISED};
        border: 1px solid {LINE};
        border-radius: 6px;
        margin-top: 9px;
        padding: 10px 12px 12px 12px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 11px;
        padding: 0 4px;
        color: {FG_DIM};
        font-size: 9pt;
    }}

    QPushButton {{
        background: {BG_RAISED};
        border: 1px solid {LINE};
        border-radius: 5px;
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        border-color: {ACCENT_DIM};
    }}
    QPushButton:pressed {{
        background: {BG_INPUT};
    }}
    QPushButton:disabled {{
        color: {FG_DIM};
        border-color: {BG_RAISED};
    }}
    QPushButton#primary {{
        background: {ACCENT_DIM};
        border-color: {ACCENT};
        font-weight: 600;
    }}

    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {{
        background: {BG_INPUT};
        border: 1px solid {LINE};
        border-radius: 5px;
        padding: 5px 8px;
        selection-background-color: {ACCENT_DIM};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 18px;
    }}
    QComboBox QAbstractItemView {{
        background: {BG_RAISED};
        border: 1px solid {LINE};
        selection-background-color: {ACCENT_DIM};
    }}

    QTableWidget {{
        background: {BG_INPUT};
        alternate-background-color: {BG_RAISED};
        gridline-color: {LINE};
        border: 1px solid {LINE};
        border-radius: 5px;
        font-family: "{mono}";
    }}
    QHeaderView::section {{
        background: {BG_RAISED};
        color: {FG_DIM};
        border: none;
        border-bottom: 1px solid {LINE};
        padding: 6px;
        font-family: "{ui}";
    }}

    QTextBrowser {{
        background: {BG_INPUT};
        border: 1px solid {LINE};
        border-radius: 5px;
        padding: 8px;
    }}

    QProgressBar {{
        background: {BG_INPUT};
        border: 1px solid {LINE};
        border-radius: 5px;
        text-align: center;
        font-family: "{mono}";
    }}
    QProgressBar::chunk {{
        background: {ACCENT_DIM};
        border-radius: 4px;
    }}

    QSlider::groove:horizontal {{
        height: 4px;
        background: {LINE};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {ACCENT};
        width: 12px;
        margin: -5px 0;
        border-radius: 6px;
    }}

    QCheckBox::indicator {{
        width: 15px;
        height: 15px;
        border: 1px solid {LINE};
        border-radius: 3px;
        background: {BG_INPUT};
    }}
    QCheckBox::indicator:checked {{
        background: {ACCENT};
        border-color: {ACCENT};
    }}

    QScrollBar:vertical, QScrollBar:horizontal {{
        background: transparent;
        width: 10px;
        height: 10px;
    }}
    QScrollBar::handle {{
        background: {LINE};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        height: 0;
        width: 0;
    }}
    """


def palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor(BG))
    p.setColor(QPalette.WindowText, QColor(FG))
    p.setColor(QPalette.Base, QColor(BG_INPUT))
    p.setColor(QPalette.AlternateBase, QColor(BG_RAISED))
    p.setColor(QPalette.Text, QColor(FG))
    p.setColor(QPalette.Button, QColor(BG_RAISED))
    p.setColor(QPalette.ButtonText, QColor(FG))
    p.setColor(QPalette.Highlight, QColor(ACCENT))
    p.setColor(QPalette.HighlightedText, QColor("#10131a"))
    p.setColor(QPalette.ToolTipBase, QColor(BG_RAISED))
    p.setColor(QPalette.ToolTipText, QColor(FG))
    return p


def apply(app) -> None:
    app.setStyle("Fusion")
    app.setPalette(palette())
    font = QFont(ui_family(), 10)
    font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(font)
    app.setStyleSheet(stylesheet())

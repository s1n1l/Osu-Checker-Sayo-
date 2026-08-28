"""Small building blocks shared by the tabs.

Qt has no card, no badge and no banner, and hand rolling them in every tab
is how a window ends up looking like a settings dialog from 2003. They
live here once so spacing, radii and colour stay the same everywhere.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton,
                               QSizePolicy, QTextBrowser, QVBoxLayout, QWidget)

from ..device.keys import IGNORED, key_name
from . import theme


def dim_label(text: str, wrap: bool = True) -> QLabel:
    label = QLabel(text)
    label.setObjectName("dim")
    label.setWordWrap(wrap)
    return label


def muted_label(text: str, wrap: bool = True) -> QLabel:
    label = QLabel(text)
    label.setObjectName("muted")
    label.setWordWrap(wrap)
    return label


def section_label(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setObjectName("section")
    return label


class Card(QFrame):
    """A titled panel. Content goes into `body`."""

    def __init__(self, title: str = "", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 14)
        outer.setSpacing(9)
        if title:
            outer.addWidget(section_label(title))
        if subtitle:
            outer.addWidget(muted_label(subtitle))
        self.body = QVBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(8)
        outer.addLayout(self.body)

    def add(self, widget: QWidget, stretch: int = 0) -> QWidget:
        self.body.addWidget(widget, stretch)
        return widget


class StatTile(QFrame):
    """Caption, one figure, one line of context."""

    def __init__(self, caption: str, value: str = "—", hint: str = "",
                 tone: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("tile")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 11, 14, 12)
        lay.setSpacing(3)

        # Wrapping matters: a long caption otherwise sets a minimum width
        # that no amount of layout can get back.
        self.caption = QLabel(caption)
        self.caption.setObjectName("section")
        self.caption.setWordWrap(True)
        lay.addWidget(self.caption)

        self.value = QLabel(value)
        self.value.setObjectName("value")
        lay.addWidget(self.value)

        self.hint = QLabel(hint)
        self.hint.setObjectName("muted")
        self.hint.setWordWrap(True)
        self.hint.setVisible(bool(hint))
        lay.addWidget(self.hint)

        self._tone = None
        self.set_tone(tone)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)

    def set_value(self, text: str, tone: str = "") -> None:
        self.value.setText(text)
        self.set_tone(tone)

    def set_hint(self, text: str) -> None:
        self.hint.setText(text)
        self.hint.setVisible(bool(text))

    def set_tone(self, tone: str) -> None:
        # setStyleSheet re-parses and re-polishes the widget, which is far
        # too expensive to do on every refresh of a live readout.
        if tone == self._tone:
            return
        self._tone = tone
        colour = {"good": theme.GOOD, "warn": theme.WARN,
                  "bad": theme.BAD, "accent": theme.ACCENT}.get(tone, "")
        self.value.setStyleSheet(f"color: {colour};" if colour else "")


class Badge(QLabel):
    """A small pill, used for severity and priority."""

    def __init__(self, text: str, colour: str = theme.ACCENT, parent=None):
        super().__init__(text, parent)
        self.set_colour(colour)
        font = self.font()
        font.setPointSize(max(8, font.pointSize() - 1))
        font.setWeight(QFont.DemiBold)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)

    def set_colour(self, colour: str) -> None:
        self.setStyleSheet(
            f"color: {colour}; border: 1px solid {colour}; border-radius: 7px;"
            f"padding: 2px 9px; background: transparent;")


class Banner(QFrame):
    """One line of context above a view: a note or a warning."""

    def __init__(self, text: str = "", kind: str = "info", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 9, 12, 9)
        lay.setSpacing(10)
        self.mark = QLabel("")
        self.mark.setFixedWidth(14)
        lay.addWidget(self.mark, 0, Qt.AlignTop)
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        lay.addWidget(self.label, 1)
        self.set_text(text, kind)

    def set_text(self, text: str, kind: str = "info") -> None:
        self.setObjectName("bannerWarn" if kind == "warn" else "banner")
        self.style().unpolish(self)
        self.style().polish(self)
        self.mark.setText("!" if kind == "warn" else "i")
        self.mark.setStyleSheet(
            f"color: {theme.WARN if kind == 'warn' else theme.ACCENT};"
            f"font-weight: 600;")
        self.label.setText(text)
        self.setVisible(bool(text))


class AutoTextBrowser(QTextBrowser):
    """A rich text pane that grows to its content instead of scrolling.

    Nested scroll areas are miserable to use, and every explanatory panel
    in this app sits inside a column that already scrolls.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.document().contentsChanged.connect(self._resize)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize()

    def _resize(self):
        self.document().setTextWidth(max(1, self.viewport().width()))
        height = int(self.document().size().height()) + 2 * int(
            self.frameWidth()) + 20
        if height != self.minimumHeight():
            self.setMinimumHeight(height)
            self.setMaximumHeight(height)


def rich_text(flat: bool = False, auto_height: bool = False) -> QTextBrowser:
    """A read-only rich text pane with the app's document styling."""
    view = AutoTextBrowser() if auto_height else QTextBrowser()
    view.setOpenExternalLinks(False)
    if flat:
        view.setObjectName("flat")
    view.document().setDefaultStyleSheet(document_css())
    return view


def document_css() -> str:
    return f"""
    body {{ color: {theme.FG}; }}
    p {{ margin: 0 0 8px 0; line-height: 148%; }}
    b {{ color: {theme.FG}; }}
    .lead {{ color: {theme.FG_DIM}; }}
    .dim {{ color: {theme.FG_DIM}; }}
    .muted {{ color: {theme.FG_MUTED}; }}
    .good {{ color: {theme.GOOD}; }}
    .warn {{ color: {theme.WARN}; }}
    .bad {{ color: {theme.BAD}; }}
    .accent {{ color: {theme.ACCENT}; }}
    .kicker {{ font-weight: 600; letter-spacing: 0.6px; }}
    .title {{ font-weight: 600; font-size: 11pt; }}
    .action {{ color: {theme.GOOD}; }}
    .block {{ margin-bottom: 16px; }}
    td {{ padding: 3px 10px 3px 0; }}
    th {{ color: {theme.FG_DIM}; text-align: left; padding: 3px 10px 3px 0; }}
    """


class KeyCaptureButton(QPushButton):
    """Press it, then press the key you want bound to this device slot."""

    captured = Signal(int)

    def __init__(self, code: int, prompt: str, parent=None):
        super().__init__(parent)
        self.setObjectName("capture")
        self.setCheckable(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.prompt = prompt
        self.code = code
        self.setMinimumWidth(130)
        self.clicked.connect(self._toggled)
        self._show()

    def set_code(self, code: int) -> None:
        self.code = code
        self._show()

    def _show(self) -> None:
        self.setText(self.prompt if self.isChecked() else key_name(self.code))

    def _toggled(self) -> None:
        self._show()
        if self.isChecked():
            self.grabKeyboard()
        else:
            self.releaseKeyboard()

    def keyPressEvent(self, event) -> None:
        if not self.isChecked():
            super().keyPressEvent(event)
            return
        code = event.nativeVirtualKey()
        if event.key() == Qt.Key_Escape or code in IGNORED:
            self._cancel()
            return
        self.code = int(code)
        self._cancel()
        self.captured.emit(self.code)

    def _cancel(self) -> None:
        self.setChecked(False)
        self.releaseKeyboard()
        self._show()

    def focusOutEvent(self, event) -> None:
        if self.isChecked():
            self._cancel()
        super().focusOutEvent(event)

"""The scrolling note lane the trainer plays through.

Painted by hand rather than with pyqtgraph. There are only a few dozen
shapes on screen, and a plain paintEvent costs a fraction of a millisecond
where a plot costs ten -- which matters here, because every millisecond
the GUI thread spends is a millisecond the thread timing key presses is
not running.

Time runs left to right. Notes arrive from the right and are judged as
they cross the hit line; what is behind the line is what already happened.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from . import theme

PAST_MS = 700.0
AHEAD_MS = 1700.0
SPAN_MS = PAST_MS + AHEAD_MS
NOTE_R = 9.0
OPENER_R = 12.0
# Judging runs slower than the frames, so a note that has just been
# answered would otherwise flash red for a frame or two before the verdict
# catches up with it.
JUDGE_GRACE_MS = 120.0


class NoteLane(QWidget):
    """Shows the rhythm being asked for, and how it is being answered."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(132)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.notes: list[float] = []
        self.openers: set[int] = set()
        self.matched: dict[int, float] = {}
        self.presses: list[tuple[float, str]] = []
        self.beat = 333.0
        self.window = 100.0
        self.now = 0.0
        self.active = False
        self._first = 0

    def set_rhythm(self, notes, openers, beat: float, window: float) -> None:
        self.notes = notes
        self.openers = openers
        self.beat = beat
        self.window = window
        self.matched = {}
        self.presses = []
        self._first = 0
        self.update()

    def set_now(self, now: float) -> None:
        """Scrolling only: cheap enough to run every frame."""
        self.now = now
        self.update()

    def set_judged(self, matched, presses, active: bool) -> None:
        """Judging is slower, so it arrives a couple of frames apart."""
        self.matched = matched
        self.presses = presses
        self.active = active

    # drawing ------------------------------------------------------------

    def _x(self, t: float) -> float:
        return (t - (self.now - PAST_MS)) / SPAN_MS * self.width()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = QRectF(0, 0, self.width(), self.height())
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(theme.BG_PANEL))
        painter.drawRoundedRect(rect, 10, 10)

        mid = self.height() * 0.46
        hit_x = self._x(self.now)

        if not self.notes:
            painter.setPen(QColor(theme.FG_MUTED))
            painter.drawText(rect, Qt.AlignCenter, self._idle_text)
            return

        # beats, so the rests have a scale to be read against
        painter.setPen(QPen(QColor(theme.LINE_SOFT), 1))
        start = self.notes[0]
        first_beat = start + self.beat * int(
            (self.now - PAST_MS - start) / self.beat)
        tick = first_beat
        while tick < self.now + AHEAD_MS:
            x = self._x(tick)
            painter.drawLine(QPointF(x, mid - 34), QPointF(x, mid + 34))
            tick += self.beat

        # the line notes are judged on
        painter.setPen(QPen(QColor(theme.FG), 2))
        painter.drawLine(QPointF(hit_x, 8), QPointF(hit_x, self.height() - 8))

        lo = self.now - PAST_MS
        hi = self.now + AHEAD_MS
        # the first index still on screen, carried between frames
        while self._first < len(self.notes) and self.notes[self._first] < lo:
            self._first += 1
        index = max(0, self._first - 1)
        while index < len(self.notes) and self.notes[index] <= hi:
            self._draw_note(painter, index, mid)
            index += 1

        # what was actually pressed, under the lane
        base = self.height() - 14
        for when, side in self.presses:
            if not lo <= when <= hi:
                continue
            colour = QColor(theme.HAND_LEFT if side == "left"
                            else theme.HAND_RIGHT)
            painter.setPen(QPen(colour, 2))
            x = self._x(when)
            painter.drawLine(QPointF(x, base - 9), QPointF(x, base))

    def _draw_note(self, painter: QPainter, index: int, mid: float) -> None:
        note = self.notes[index]
        x = self._x(note)
        opener = index in self.openers
        radius = OPENER_R if opener else NOTE_R
        error = self.matched.get(index)

        if error is not None:
            colour = QColor(self._tone(abs(error)))
            painter.setPen(QPen(colour, 2))
            painter.setBrush(QColor(colour.red(), colour.green(),
                                    colour.blue(), 90))
        elif note < self.now - self.window - JUDGE_GRACE_MS and self.active:
            colour = QColor(theme.BAD)                  # gone unanswered
            painter.setPen(QPen(colour, 2, Qt.DotLine))
            painter.setBrush(Qt.NoBrush)
        else:
            colour = QColor(theme.ACCENT if opener else theme.FG_DIM)
            painter.setPen(QPen(colour, 2))
            painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(x, mid), radius, radius)

    def _tone(self, error: float) -> str:
        if error <= self.window * 0.25:
            return theme.GOOD
        if error <= self.window * 0.55:
            return theme.WARN
        return theme.BAD

    _idle_text = ""

    def set_idle_text(self, text: str) -> None:
        self._idle_text = text
        self.update()

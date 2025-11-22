# ui/history_view.py

from __future__ import annotations

from datetime import datetime
from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QHBoxLayout,
    QFrame,
)

from core.storage import load_all_sessions
from core.models import WritingSession
from ui.session_detail_dialog import SessionDetailDialog


class HistoryView(QWidget):
    """
    Past sessions list, styled like the design mock:
    - white background
    - big title in the main header (provided by MainWindow)
    - each item: title, date, mode badge on the right
    """

    sessionsChanged = pyqtSignal()  # still here for future deletions etc.

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HistoryViewRoot")

        self._build_ui()
        self._apply_style()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setSpacing(0)

        # scroll area so the list can grow
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("HistoryScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.inner = QWidget()
        self.inner.setObjectName("HistoryInner")
        self.inner_layout = QVBoxLayout(self.inner)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(0)

        self.scroll_area.setWidget(self.inner)
        outer.addWidget(self.scroll_area)

    def _clear_items(self) -> None:
        layout = self.inner_layout

        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue  # silent pylance warning

            w = item.widget()
            if w is not None:
                w.deleteLater()

    # ------------------------------------------------------------------ Public API

    def refresh(self) -> None:
        """Reload all sessions and rebuild the list UI."""
        sessions: List[WritingSession] = load_all_sessions()

        # sort newest first
        sessions.sort(
            key=lambda s: (
                s.session_date,
                s.start_time or datetime.min,
            ),
            reverse=True,
        )

        self._clear_items()

        if not sessions:
            # simple empty state label
            empty = QLabel("No sessions yet. Start a new one to see it here.")
            empty.setObjectName("EmptyHistoryLabel")
            empty.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self.inner_layout.addWidget(empty)
            self.inner_layout.addStretch()
            return

        for idx, sess in enumerate(sessions):
            card = self._make_card(sess)
            self.inner_layout.addWidget(card)

            # separator line between rows
            if idx < len(sessions) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Plain)
                line.setObjectName("HistoryDivider")
                self.inner_layout.addWidget(line)

        self.inner_layout.addStretch()

    # ------------------------------------------------------------------ Card creation

    def _make_card(self, sess: WritingSession) -> QWidget:
        card = QWidget()
        card.setObjectName("SessionCard")

        row = QHBoxLayout(card)
        row.setContentsMargins(0, 16, 0, 16)
        row.setSpacing(16)

        # left: title + date
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(4)

        title = sess.title or sess.session_date.isoformat()
        title_label = QLabel(title)
        title_label.setObjectName("SessionTitle")

        date_label = QLabel(sess.session_date.strftime("%m/%d/%Y"))
        date_label.setObjectName("SessionDate")

        text_col.addWidget(title_label)
        text_col.addWidget(date_label)

        # right: mode badge
        mode_label = QLabel(self._mode_label(sess.mode))
        mode_label.setObjectName("SessionModeBadge")
        mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row.addLayout(text_col, 1)
        row.addStretch()
        row.addWidget(mode_label, 0, Qt.AlignmentFlag.AlignVCenter)

        # simple click-to-open behavior
        def _open_detail(event):
            if event.button() == Qt.MouseButton.LeftButton:
                dlg = SessionDetailDialog(sess, self)
                dlg.exec()

        card.mousePressEvent = _open_detail  # type: ignore[assignment]

        return card

    @staticmethod
    def _mode_label(mode: str | None) -> str:
        if mode == "free":
            return "FREE"
        if mode == "random_topic":
            return "AI PROMPT"
        return (mode or "").upper()

    # ------------------------------------------------------------------ Styling

    def _apply_style(self) -> None:
        self.setStyleSheet("""
        QWidget#HistoryViewRoot {
            background-color: #ffffff;
        }
        QWidget#HistoryInner {
            background-color: #000000;
        }
        QScrollArea#HistoryScrollArea {
            background: transparent;
            border: none;
        }

        QLabel#EmptyHistoryLabel {
            font-size: 14px;
            color: #888888;
        }

        QWidget#SessionCard {
            background-color: #000000;
        }

        QLabel#SessionTitle {
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
        }

        QLabel#SessionDate {
            font-size: 13px;
            color: #bbbbbb;
        }

        QLabel#SessionModeBadge {
            background-color: #c8c8c8;
            color: #000000;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 14px;
            border-radius: 3px;
        }

        QFrame#HistoryDivider {
            background-color: #e5e5e5;
            max-height: 1px;
            min-height: 1px;
        }
        """)

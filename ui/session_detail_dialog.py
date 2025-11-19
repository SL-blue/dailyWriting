# ui/session_detail_dialog.py

from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QDialogButtonBox,
    QWidget,
)
from PyQt6.QtCore import Qt

from core.models import WritingSession


def _format_time(dt: Optional[datetime]) -> str:
    if dt is None:
        return "-"
    # show local time as HH:MM
    return dt.strftime("%H:%M")


def _format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0 min"
    minutes = seconds // 60
    secs = seconds % 60
    if minutes > 0:
        return f"{minutes} min {secs:02d} s"
    return f"{secs} s"


class SessionDetailDialog(QDialog):
    """
    Read-only detail view for a single WritingSession.
    Shows metadata (date, mode, topic, duration, counts) + full content.
    """

    def __init__(self, session: WritingSession, parent: QWidget | None = None):
        super().__init__(parent)
        self.session = session

        self.setWindowTitle(f"Session on {session.session_date.isoformat()}")
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        # --- Top: metadata ---
        meta_layout = QVBoxLayout()
        layout.addLayout(meta_layout)

        # First row: date + mode
        row1 = QHBoxLayout()
        date_label = QLabel(f"Date: {session.session_date.isoformat()}")
        mode_str = "Free writing" if session.mode == "free" else "Random topic"
        mode_label = QLabel(f"Mode: {mode_str}")
        row1.addWidget(date_label)
        row1.addStretch()
        row1.addWidget(mode_label)
        meta_layout.addLayout(row1)

        # Second row: topic (if any)
        if session.topic:
            topic_label = QLabel(f"Topic: {session.topic}")
        else:
            topic_label = QLabel("Topic: (none)")
        topic_label.setWordWrap(True)
        meta_layout.addWidget(topic_label)

        # Third row: duration + time range
        row3 = QHBoxLayout()
        duration_label = QLabel(f"Duration: {_format_duration(session.duration_seconds)}")
        time_label = QLabel(
            f"Time: {_format_time(session.start_time)} – {_format_time(session.end_time)}"
        )
        row3.addWidget(duration_label)
        row3.addStretch()
        row3.addWidget(time_label)
        meta_layout.addLayout(row3)

        # Fourth row: counts
        row4 = QHBoxLayout()
        counts_label = QLabel(
            f"Chars: {session.char_count}    Words: {session.word_count}"
        )
        row4.addWidget(counts_label)
        row4.addStretch()
        meta_layout.addLayout(row4)

        # --- Separator: optional, can be styled later ---
        # You can add a line or leave as-is.

        # --- Main content: full text ---
        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setPlainText(session.content)
        layout.addWidget(self.editor)

        # --- Buttons: Close ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Basic alignment / style hooks
        for lbl in (date_label, mode_label, topic_label, duration_label, time_label, counts_label):
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

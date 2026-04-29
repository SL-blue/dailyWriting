# ui/session_detail_dialog.py

from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QDialogButtonBox,
    QWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from core.models import WritingSession
from core.export import export_session, get_export_extension
from core.config import get_settings
from core.logging_config import get_logger

logger = get_logger("session_detail_dialog")


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

        # --- Buttons: Export + Close ---
        button_layout = QHBoxLayout()

        self.export_button = QPushButton("Export...")
        self.export_button.clicked.connect(self._on_export)
        button_layout.addWidget(self.export_button)

        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        # Basic alignment / style hooks
        for lbl in (date_label, mode_label, topic_label, duration_label, time_label, counts_label):
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def _on_export(self):
        """Handle export button click."""
        settings = get_settings()
        default_format = settings.export.default_format
        include_metadata = settings.export.include_metadata

        # Build filter string for file dialog
        filters = {
            "markdown": "Markdown Files (*.md)",
            "txt": "Text Files (*.txt)",
            "json": "JSON Files (*.json)",
            "html": "HTML Files (*.html)",
        }

        # Put default format first
        filter_list = [filters[default_format]]
        for fmt, filter_str in filters.items():
            if fmt != default_format:
                filter_list.append(filter_str)
        filter_string = ";;".join(filter_list)

        # Generate default filename
        safe_title = "".join(c for c in self.session.title if c.isalnum() or c in " -_").strip()
        safe_title = safe_title[:50] or "session"
        default_name = f"{self.session.session_date.isoformat()}_{safe_title}{get_export_extension(default_format)}"

        # Get last export path or use home directory
        start_dir = settings.export.last_export_path or str(Path.home())
        start_path = str(Path(start_dir) / default_name)

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Session",
            start_path,
            filter_string
        )

        if not file_path:
            return

        # Determine format from selected filter
        format_map = {v: k for k, v in filters.items()}
        export_format = format_map.get(selected_filter, default_format)

        try:
            export_session(
                self.session,
                Path(file_path),
                format=export_format,
                include_metadata=include_metadata
            )

            # Save last export directory
            settings.export.last_export_path = str(Path(file_path).parent)
            settings.save()

            QMessageBox.information(
                self,
                "Export Successful",
                f"Session exported to:\n{file_path}"
            )
            logger.info("Session exported: %s", file_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export session:\n{e}"
            )
            logger.error("Export failed: %s", e)

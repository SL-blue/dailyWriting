# ui/history_view.py

from typing import List

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal

from core.models import WritingSession
from core.storage import load_all_sessions, delete_session
from core.streak_days import maybe_unmark_today_if_empty
from ui.session_detail_dialog import SessionDetailDialog


class HistoryView(QWidget):
    # Emitted whenever sessions are deleted (so MainWindow can refresh calendar/streak)
    sessionsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        root_layout = QHBoxLayout()
        self.setLayout(root_layout)

        # --- Left panel: list of all sessions ---
        self.list = QListWidget()
        self.list.setMinimumWidth(320)
        root_layout.addWidget(self.list)

        # --- Right panel: preview + actions ---
        right = QVBoxLayout()
        root_layout.addLayout(right)

        self.title_label = QLabel("Session Preview")
        right.addWidget(self.title_label)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        right.addWidget(self.preview)

        self.delete_button = QPushButton("Delete Session")
        self.delete_button.setEnabled(False)
        right.addWidget(self.delete_button)

        right.addStretch()

        self.sessions: List[WritingSession] = []

        # connections
        self.list.currentRowChanged.connect(self._on_row_changed)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.list.itemDoubleClicked.connect(self._on_item_double_clicked)

        # initial load
        self.refresh()

    def refresh(self):
        """Reload all sessions and rebuild the list."""
        self.sessions = sorted(
            load_all_sessions(),
            key=lambda s: (s.session_date, s.start_time),
            reverse=True,
        )

        self.list.clear()

        for sess in self.sessions:
            day = sess.session_date.isoformat()
            mode = "Free" if sess.mode == "free" else "Topic"
            preview = sess.content.strip().replace("\n", " ")
            if len(preview) > 40:
                preview = preview[:40] + "…"
            item = QListWidgetItem(f"{day} — [{mode}] {preview}")
            self.list.addItem(item)

        if self.sessions:
            self.list.setCurrentRow(0)
        else:
            self.preview.clear()
            self.delete_button.setEnabled(False)

    def _on_row_changed(self, row: int):
        """Update preview when selection changes."""
        if row < 0 or row >= len(self.sessions):
            self.preview.clear()
            self.delete_button.setEnabled(False)
            return

        sess = self.sessions[row]
        # You can add metadata here later (date, duration, etc.)
        self.preview.setPlainText(sess.content)
        self.delete_button.setEnabled(True)

    def _on_delete_clicked(self):
        """Delete the currently selected session (with confirmation)."""
        row = self.list.currentRow()
        if row < 0 or row >= len(self.sessions):
            return

        sess = self.sessions[row]

        # Confirm
        reply = QMessageBox.question(
            self,
            "Delete Session",
            "Are you sure you want to delete this session?\n"
            "This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete from disk
        delete_session(sess)

        # Update streak days: only unmark if it's today AND no sessions left today
        maybe_unmark_today_if_empty(sess.session_date)

        # Refresh our own list
        self.refresh()

        # Notify MainWindow so calendar/streak can update
        self.sessionsChanged.emit()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Open a detail dialog for the double-clicked session."""
        row = self.list.row(item)
        if row < 0 or row >= len(self.sessions):
            return

        sess = self.sessions[row]
        dlg = SessionDetailDialog(sess, self)
        dlg.exec()


# ui/session_list_dialog.py

from datetime import date
from typing import List

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QDialogButtonBox,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from core.models import WritingSession
from core.storage import load_sessions_for_date, delete_session
from core.streak_days import maybe_unmark_today_if_empty
from ui.session_detail_dialog import SessionDetailDialog   # <-- NEW


class SessionListDialog(QDialog):
    """
    Dialog for reviewing all sessions on a given day.
    Allows viewing content, double-click to open detail view,
    and deleting sessions.
    """

    def __init__(self, day: date, parent=None):
        super().__init__(parent)
        self._day = day
        self._sessions: List[WritingSession] = []

        self.setWindowTitle(f"Sessions on {day.isoformat()}")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # List of sessions for this day
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Preview of selected session
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview)

        # Delete button
        self.delete_button = QPushButton("Delete Selected Session")
        self.delete_button.setEnabled(False)
        layout.addWidget(self.delete_button)

        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Connections
        self.list_widget.currentRowChanged.connect(self._on_row_changed)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)  # <-- NEW

        # Initial load
        self._load_sessions()

    def _load_sessions(self):
        """Load/reload all sessions for this day and refresh the UI."""
        self._sessions = load_sessions_for_date(self._day)
        self.list_widget.clear()
        self.preview.clear()
        self.delete_button.setEnabled(False)

        for sess in self._sessions:
            mode = "Free" if sess.mode == "free" else "Topic"
            preview = sess.content.strip().replace("\n", " ")
            if len(preview) > 40:
                preview = preview[:40] + "…"
            item = QListWidgetItem(f"[{mode}] {preview}")
            self.list_widget.addItem(item)

        if self._sessions:
            self.list_widget.setCurrentRow(0)
        else:
            # No sessions left for this day – close dialog
            self.accept()

    def _on_row_changed(self, row: int):
        """Update preview + delete button when selection changes."""
        if row < 0 or row >= len(self._sessions):
            self.preview.clear()
            self.delete_button.setEnabled(False)
            return

        sess = self._sessions[row]
        self.preview.setPlainText(sess.content)
        self.delete_button.setEnabled(True)

    def _on_delete_clicked(self):
        """Delete the currently selected session (with confirmation)."""
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self._sessions):
            return

        sess = self._sessions[row]

        reply = QMessageBox.question(
            self,
            "Delete Session",
            "Are you sure you want to delete this session?\n"
            "This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete JSON file
        delete_session(sess)

        # Adjust streak only if this is today's last session
        maybe_unmark_today_if_empty(sess.session_date)

        # Reload sessions for this day (auto-closes if none left)
        self._load_sessions()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Open detail dialog for the double-clicked session."""
        row = self.list_widget.row(item)
        if row < 0 or row >= len(self._sessions):
            return

        sess = self._sessions[row]
        dlg = SessionDetailDialog(sess, self)
        dlg.exec()

# ui/shortcuts_dialog.py

"""
Keyboard shortcuts reference dialog.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QWidget,
    QGridLayout,
)
from PyQt6.QtCore import Qt


class ShortcutRow(QFrame):
    """A single shortcut row showing key combo and description."""

    def __init__(self, shortcut: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("ShortcutRow")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)

        # Shortcut key
        key_label = QLabel(shortcut)
        key_label.setObjectName("ShortcutKey")
        key_label.setFixedWidth(100)
        layout.addWidget(key_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setObjectName("ShortcutDesc")
        layout.addWidget(desc_label, 1)


class ShortcutsDialog(QDialog):
    """Dialog showing all keyboard shortcuts."""

    SHORTCUTS = {
        "Sessions": [
            ("⌘N", "New free writing session"),
            ("⇧⌘N", "New AI prompt session"),
            ("⌘Return", "Finish current session"),
            ("Esc", "Cancel/close dialog"),
        ],
        "Navigation": [
            ("⌘1", "Go to Calendar view"),
            ("⌘2", "Go to Sessions view"),
            ("⌘3", "Go to Statistics view"),
        ],
        "Application": [
            ("⌘,", "Open Settings"),
            ("⌘E", "Export session"),
            ("⌘Q", "Quit application"),
        ],
        "Editing": [
            ("⌘Z", "Undo"),
            ("⇧⌘Z", "Redo"),
            ("⌘X", "Cut"),
            ("⌘C", "Copy"),
            ("⌘V", "Paste"),
            ("⌘A", "Select all"),
        ],
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ShortcutsDialog")
        self.setWindowTitle("Keyboard Shortcuts")
        self.setFixedSize(450, 500)
        self.setModal(True)

        self._build_ui()

    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title_label = QLabel("Keyboard Shortcuts")
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("ShortcutsScroll")

        content = QWidget()
        content.setObjectName("ShortcutsContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # Add shortcut sections
        for section_name, shortcuts in self.SHORTCUTS.items():
            section_label = QLabel(section_name.upper())
            section_label.setObjectName("SectionTitle")
            content_layout.addWidget(section_label)

            for shortcut, description in shortcuts:
                row = ShortcutRow(shortcut, description)
                content_layout.addWidget(row)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setObjectName("CloseButton")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)


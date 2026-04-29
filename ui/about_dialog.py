# ui/about_dialog.py

"""
About dialog showing application information.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Version info
__version__ = "1.0.0"
__app_name__ = "DailyWriting"


class AboutDialog(QDialog):
    """About dialog showing app information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {__app_name__}")
        self.setFixedSize(400, 300)
        self.setModal(True)

        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # App name
        name_label = QLabel(__app_name__)
        name_label.setObjectName("AppName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(f"Version {__version__}")
        version_label.setObjectName("Version")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("Separator")
        layout.addWidget(separator)

        # Description
        desc_label = QLabel(
            "A distraction-free writing app for daily practice.\n\n"
            "Build your writing habit with streaks, AI-generated\n"
            "prompts, and detailed statistics."
        )
        desc_label.setObjectName("Description")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addStretch()

        # Credits
        credits_label = QLabel("Made with PyQt6 and Google Gemini")
        credits_label.setObjectName("Credits")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits_label)

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

    def _apply_style(self):
        """Apply styling to the dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }

            QLabel#AppName {
                color: #00b894;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#Version {
                color: #888888;
                font-size: 14px;
            }

            QFrame#Separator {
                background-color: #333333;
                max-height: 1px;
            }

            QLabel#Description {
                color: #cccccc;
                font-size: 14px;
                line-height: 1.5;
            }

            QLabel#Credits {
                color: #666666;
                font-size: 12px;
            }

            QPushButton#CloseButton {
                background-color: #00b894;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#CloseButton:hover {
                background-color: #00a383;
            }
            QPushButton#CloseButton:pressed {
                background-color: #009274;
            }
        """)

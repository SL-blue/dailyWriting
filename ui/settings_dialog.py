# ui/settings_dialog.py

"""
Settings dialog with tabbed interface for configuring DailyWriting.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QCheckBox,
    QPushButton,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.config import AppSettings, get_settings
from core.logging_config import get_logger

logger = get_logger("settings_dialog")


class SettingsDialog(QDialog):
    """Settings dialog with tabs for different setting categories."""

    settingsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self.settings = get_settings()

        self._build_ui()
        self._load_settings()
        self._apply_style()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        self.setLayout(layout)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.tabs.addTab(self._create_general_tab(), "General")
        self.tabs.addTab(self._create_ai_tab(), "AI")
        self.tabs.addTab(self._create_export_tab(), "Export")
        self.tabs.addTab(self._create_appearance_tab(), "Appearance")

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._on_reset)
        button_layout.addWidget(self.reset_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _create_general_tab(self) -> QWidget:
        """Create the General settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        widget.setLayout(layout)

        # Writing settings group
        writing_group = QGroupBox("Writing")
        writing_layout = QFormLayout()
        writing_group.setLayout(writing_layout)

        self.default_mode_combo = QComboBox()
        self.default_mode_combo.addItem("Free Writing", "free")
        self.default_mode_combo.addItem("Random Topic (AI)", "random_topic")
        writing_layout.addRow("Default mode:", self.default_mode_combo)

        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(10, 300)
        self.autosave_spin.setSuffix(" seconds")
        writing_layout.addRow("Auto-save interval:", self.autosave_spin)

        layout.addWidget(writing_group)

        # Goals group
        goals_group = QGroupBox("Goals")
        goals_layout = QFormLayout()
        goals_group.setLayout(goals_layout)

        self.word_goal_spin = QSpinBox()
        self.word_goal_spin.setRange(0, 10000)
        self.word_goal_spin.setSpecialValueText("No goal")
        self.word_goal_spin.setSuffix(" words")
        goals_layout.addRow("Daily word goal:", self.word_goal_spin)

        self.show_goal_check = QCheckBox("Show goal progress in session")
        goals_layout.addRow("", self.show_goal_check)

        layout.addWidget(goals_group)
        layout.addStretch()

        return widget

    def _create_ai_tab(self) -> QWidget:
        """Create the AI settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        widget.setLayout(layout)

        # Model settings group
        model_group = QGroupBox("Topic Generation")
        model_layout = QFormLayout()
        model_group.setLayout(model_layout)

        self.model_combo = QComboBox()
        self.model_combo.addItem("Gemini 2.5 Flash (Recommended)", "gemini-2.5-flash")
        self.model_combo.addItem("Gemini 2.5 Pro", "gemini-2.5-pro")
        model_layout.addRow("Model:", self.model_combo)

        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 5)
        model_layout.addRow("Retry attempts:", self.retry_spin)

        layout.addWidget(model_group)

        # API info
        info_group = QGroupBox("API Configuration")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)

        info_label = QLabel(
            "The Google API key is read from the GOOGLE_API_KEY environment variable.\n\n"
            "To set it, add this to your shell profile (~/.zshrc or ~/.bashrc):\n"
            "export GOOGLE_API_KEY='your-api-key-here'"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888888; font-size: 13px;")
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)
        layout.addStretch()

        return widget

    def _create_export_tab(self) -> QWidget:
        """Create the Export settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        widget.setLayout(layout)

        # Export settings group
        export_group = QGroupBox("Export Options")
        export_layout = QFormLayout()
        export_group.setLayout(export_layout)

        self.format_combo = QComboBox()
        self.format_combo.addItem("Markdown (.md)", "markdown")
        self.format_combo.addItem("Plain Text (.txt)", "txt")
        self.format_combo.addItem("JSON (.json)", "json")
        self.format_combo.addItem("HTML (.html)", "html")
        export_layout.addRow("Default format:", self.format_combo)

        self.include_metadata_check = QCheckBox("Include metadata (date, duration, word count)")
        export_layout.addRow("", self.include_metadata_check)

        layout.addWidget(export_group)
        layout.addStretch()

        return widget

    def _create_appearance_tab(self) -> QWidget:
        """Create the Appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        widget.setLayout(layout)

        # Editor settings group
        editor_group = QGroupBox("Editor")
        editor_layout = QFormLayout()
        editor_group.setLayout(editor_layout)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(12, 32)
        self.font_size_spin.setSuffix(" px")
        editor_layout.addRow("Font size:", self.font_size_spin)

        self.line_spacing_spin = QDoubleSpinBox()
        self.line_spacing_spin.setRange(1.0, 3.0)
        self.line_spacing_spin.setSingleStep(0.1)
        self.line_spacing_spin.setDecimals(1)
        editor_layout.addRow("Line spacing:", self.line_spacing_spin)

        self.font_family_edit = QLineEdit()
        self.font_family_edit.setPlaceholderText("System default")
        editor_layout.addRow("Font family:", self.font_family_edit)

        layout.addWidget(editor_group)

        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        theme_group.setLayout(theme_layout)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark", "dark")
        # Future: self.theme_combo.addItem("Light", "light")
        theme_layout.addRow("Theme:", self.theme_combo)

        theme_note = QLabel("Additional themes coming soon.")
        theme_note.setStyleSheet("color: #888888; font-size: 12px;")
        theme_layout.addRow("", theme_note)

        layout.addWidget(theme_group)
        layout.addStretch()

        return widget

    def _load_settings(self):
        """Load current settings into the UI."""
        # General tab
        idx = self.default_mode_combo.findData(self.settings.writing.default_mode)
        if idx >= 0:
            self.default_mode_combo.setCurrentIndex(idx)
        self.autosave_spin.setValue(self.settings.writing.autosave_interval_seconds)
        self.word_goal_spin.setValue(self.settings.writing.daily_word_goal)
        self.show_goal_check.setChecked(self.settings.writing.show_word_goal)

        # AI tab
        idx = self.model_combo.findData(self.settings.ai.model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        self.retry_spin.setValue(self.settings.ai.retry_count)

        # Export tab
        idx = self.format_combo.findData(self.settings.export.default_format)
        if idx >= 0:
            self.format_combo.setCurrentIndex(idx)
        self.include_metadata_check.setChecked(self.settings.export.include_metadata)

        # Appearance tab
        self.font_size_spin.setValue(self.settings.appearance.font_size)
        self.line_spacing_spin.setValue(self.settings.appearance.line_spacing)
        self.font_family_edit.setText(self.settings.appearance.editor_font_family)
        idx = self.theme_combo.findData(self.settings.appearance.theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

    def _save_settings(self):
        """Save UI values to settings."""
        # General tab
        self.settings.writing.default_mode = self.default_mode_combo.currentData()
        self.settings.writing.autosave_interval_seconds = self.autosave_spin.value()
        self.settings.writing.daily_word_goal = self.word_goal_spin.value()
        self.settings.writing.show_word_goal = self.show_goal_check.isChecked()

        # AI tab
        self.settings.ai.model = self.model_combo.currentData()
        self.settings.ai.retry_count = self.retry_spin.value()

        # Export tab
        self.settings.export.default_format = self.format_combo.currentData()
        self.settings.export.include_metadata = self.include_metadata_check.isChecked()

        # Appearance tab
        self.settings.appearance.font_size = self.font_size_spin.value()
        self.settings.appearance.line_spacing = self.line_spacing_spin.value()
        self.settings.appearance.editor_font_family = self.font_family_edit.text().strip()
        self.settings.appearance.theme = self.theme_combo.currentData()

        self.settings.save()

    def _on_save(self):
        """Handle save button click."""
        self._save_settings()
        logger.info("Settings saved")
        self.settingsChanged.emit()
        self.accept()

    def _on_reset(self):
        """Handle reset button click."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self._load_settings()
            logger.info("Settings reset to defaults")

    def _apply_style(self):
        """Apply dialog styling."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #cccccc;
                padding: 8px 16px;
                border: 1px solid #333333;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #333333;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #cccccc;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }
            QCheckBox {
                color: #cccccc;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:default {
                background-color: #00b894;
                color: #000000;
            }
            QPushButton:default:hover {
                background-color: #00d9a5;
            }
        """)

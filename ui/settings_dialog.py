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
        self.setObjectName("SettingsDialog")
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self.settings = get_settings()

        self._build_ui()
        self._load_settings()

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

        # Provider settings group
        provider_group = QGroupBox("AI Provider")
        provider_layout = QFormLayout()
        provider_group.setLayout(provider_layout)

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("Google Gemini", "gemini")
        self.provider_combo.addItem("Anthropic Claude", "claude")
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        provider_layout.addRow("Provider:", self.provider_combo)

        layout.addWidget(provider_group)

        # Gemini settings group
        self.gemini_group = QGroupBox("Gemini Settings")
        gemini_layout = QFormLayout()
        self.gemini_group.setLayout(gemini_layout)

        self.gemini_model_combo = QComboBox()
        self.gemini_model_combo.addItem("Gemini 2.5 Pro", "gemini-2.5-pro")
        self.gemini_model_combo.addItem("Gemini 2.5 Flash", "gemini-2.5-flash")
        gemini_layout.addRow("Model:", self.gemini_model_combo)

        layout.addWidget(self.gemini_group)

        # Claude settings group
        self.claude_group = QGroupBox("Claude Settings")
        claude_layout = QFormLayout()
        self.claude_group.setLayout(claude_layout)

        self.claude_model_combo = QComboBox()
        self.claude_model_combo.addItem("Claude Sonnet 4.5", "claude-sonnet-4-5")
        self.claude_model_combo.addItem("Claude Haiku 3.5", "claude-3-5-haiku-20241022")
        claude_layout.addRow("Model:", self.claude_model_combo)

        layout.addWidget(self.claude_group)

        # General AI settings
        general_group = QGroupBox("General")
        general_layout = QFormLayout()
        general_group.setLayout(general_layout)

        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 5)
        general_layout.addRow("Retry attempts:", self.retry_spin)

        layout.addWidget(general_group)

        # API info
        info_group = QGroupBox("API Configuration")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)

        info_label = QLabel(
            "API keys are read from environment variables:\n\n"
            "For Gemini: GOOGLE_API_KEY\n"
            "For Claude: ANTHROPIC_API_KEY\n\n"
            "macOS / Linux — add to ~/.zshrc or ~/.bashrc:\n"
            "  export GOOGLE_API_KEY='your-gemini-key'\n"
            "  export ANTHROPIC_API_KEY='your-claude-key'\n\n"
            "Windows (CMD) — persists for future sessions:\n"
            "  setx GOOGLE_API_KEY \"your-gemini-key\"\n"
            "  setx ANTHROPIC_API_KEY \"your-claude-key\""
        )
        info_label.setObjectName("SettingsHint")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)
        layout.addStretch()

        return widget

    def _on_provider_changed(self, index: int):
        """Update UI when provider selection changes."""
        provider = self.provider_combo.currentData()
        self.gemini_group.setVisible(provider == "gemini")
        self.claude_group.setVisible(provider == "claude")

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
        self.theme_combo.addItem("Light", "light")
        theme_layout.addRow("Theme:", self.theme_combo)

        theme_note = QLabel("Theme switches apply immediately on Save.")
        theme_note.setObjectName("SettingsHint")
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
        idx = self.provider_combo.findData(self.settings.ai.provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        idx = self.gemini_model_combo.findData(self.settings.ai.gemini_model)
        if idx >= 0:
            self.gemini_model_combo.setCurrentIndex(idx)
        idx = self.claude_model_combo.findData(self.settings.ai.claude_model)
        if idx >= 0:
            self.claude_model_combo.setCurrentIndex(idx)
        self.retry_spin.setValue(self.settings.ai.retry_count)
        # Trigger visibility update
        self._on_provider_changed(self.provider_combo.currentIndex())

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
        self.settings.ai.provider = self.provider_combo.currentData()
        self.settings.ai.gemini_model = self.gemini_model_combo.currentData()
        self.settings.ai.claude_model = self.claude_model_combo.currentData()
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


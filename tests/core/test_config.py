"""
Tests for core/config.py - application settings.
"""

import pytest
import json
from pathlib import Path

from core.config import (
    AppSettings,
    AISettings,
    WritingSettings,
    ExportSettings,
    AppearanceSettings,
)


class TestAppSettings:
    """Tests for AppSettings dataclass."""

    def test_default_values(self):
        settings = AppSettings()

        # AI defaults
        assert settings.ai.model == "gemini-2.5-flash"
        assert settings.ai.retry_count == 3

        # Writing defaults
        assert settings.writing.default_mode == "free"
        assert settings.writing.autosave_interval_seconds == 30
        assert settings.writing.daily_word_goal == 0

        # Export defaults
        assert settings.export.default_format == "markdown"
        assert settings.export.include_metadata is True

        # Appearance defaults
        assert settings.appearance.font_size == 20
        assert settings.appearance.line_spacing == 1.5
        assert settings.appearance.theme == "dark"

    def test_save_and_load(self, tmp_path, monkeypatch):
        # Patch config file path
        config_file = tmp_path / "config.json"
        import core.config as config_module
        monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)
        monkeypatch.setattr(config_module, "CONFIG_DIR", tmp_path)

        # Create and save settings
        settings = AppSettings()
        settings.writing.daily_word_goal = 500
        settings.appearance.font_size = 24
        settings.save()

        # Verify file exists
        assert config_file.exists()

        # Load and verify
        loaded = AppSettings.load()
        assert loaded.writing.daily_word_goal == 500
        assert loaded.appearance.font_size == 24

    def test_load_missing_file(self, tmp_path, monkeypatch):
        # Patch to non-existent file
        config_file = tmp_path / "nonexistent.json"
        import core.config as config_module
        monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)

        # Should return defaults
        settings = AppSettings.load()
        assert settings.ai.model == "gemini-2.5-flash"

    def test_load_invalid_json(self, tmp_path, monkeypatch):
        # Create invalid JSON file
        config_file = tmp_path / "config.json"
        config_file.write_text("{ invalid json }")

        import core.config as config_module
        monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)

        # Should return defaults
        settings = AppSettings.load()
        assert settings.ai.model == "gemini-2.5-flash"

    def test_reset_to_defaults(self):
        settings = AppSettings()
        settings.writing.daily_word_goal = 1000
        settings.appearance.font_size = 30

        settings.reset_to_defaults()

        assert settings.writing.daily_word_goal == 0
        assert settings.appearance.font_size == 20

    def test_partial_config_file(self, tmp_path, monkeypatch):
        """Config file with only some settings should use defaults for others."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "writing": {"daily_word_goal": 750}
        }))

        import core.config as config_module
        monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)

        settings = AppSettings.load()
        assert settings.writing.daily_word_goal == 750
        # Other settings should be defaults
        assert settings.ai.model == "gemini-2.5-flash"
        assert settings.appearance.font_size == 20

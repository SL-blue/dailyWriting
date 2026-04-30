"""
Configuration management for DailyWriting application.

Uses a hybrid approach:
- QSettings for window geometry and simple UI preferences
- JSON file for complex/nested settings

Settings are stored in ~/.dailywriting/config.json
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .logging_config import get_logger
from .exceptions import ConfigError

logger = get_logger("config")

CONFIG_DIR = Path.home() / ".dailywriting"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class AISettings:
    """Settings for AI topic generation."""
    provider: str = "gemini"  # "gemini" or "claude"
    gemini_model: str = "gemini-2.5-flash"
    claude_model: str = "claude-sonnet-4-5"
    retry_count: int = 3
    # API keys are read from environment variables:
    # GOOGLE_API_KEY for Gemini, ANTHROPIC_API_KEY for Claude


@dataclass
class WritingSettings:
    """Settings for writing sessions."""
    default_mode: str = "free"  # "free" or "random_topic"
    autosave_interval_seconds: int = 30
    daily_word_goal: int = 0  # 0 = no goal
    show_word_goal: bool = False


@dataclass
class ExportSettings:
    """Settings for session export."""
    default_format: str = "markdown"  # "markdown", "txt", "json", "html"
    include_metadata: bool = True
    last_export_path: str = ""


@dataclass
class AppearanceSettings:
    """Settings for UI appearance."""
    font_size: int = 20
    line_spacing: float = 1.5
    theme: str = "dark"  # "dark" or "light"
    editor_font_family: str = ""  # Empty = system default


@dataclass
class AppSettings:
    """
    Main application settings container.

    Usage:
        settings = AppSettings.load()
        settings.writing.daily_word_goal = 500
        settings.save()
    """
    ai: AISettings = field(default_factory=AISettings)
    writing: WritingSettings = field(default_factory=WritingSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    appearance: AppearanceSettings = field(default_factory=AppearanceSettings)

    @classmethod
    def load(cls) -> "AppSettings":
        """
        Load settings from config file.
        Returns default settings if file doesn't exist or is invalid.
        """
        if not CONFIG_FILE.exists():
            logger.info("No config file found, using defaults")
            return cls()

        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)

            settings = cls(
                ai=AISettings(**data.get("ai", {})),
                writing=WritingSettings(**data.get("writing", {})),
                export=ExportSettings(**data.get("export", {})),
                appearance=AppearanceSettings(**data.get("appearance", {})),
            )
            logger.info("Settings loaded from %s", CONFIG_FILE)
            return settings

        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.warning("Failed to load config, using defaults: %s", e)
            return cls()

    def save(self) -> None:
        """Save settings to config file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        try:
            data = {
                "ai": asdict(self.ai),
                "writing": asdict(self.writing),
                "export": asdict(self.export),
                "appearance": asdict(self.appearance),
            }

            with CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info("Settings saved to %s", CONFIG_FILE)

        except OSError as e:
            logger.error("Failed to save settings: %s", e)
            raise ConfigError(f"Failed to save settings: {e}") from e

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.ai = AISettings()
        self.writing = WritingSettings()
        self.export = ExportSettings()
        self.appearance = AppearanceSettings()
        logger.info("Settings reset to defaults")


# Global settings instance (lazy-loaded)
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get the global settings instance, loading from file if needed."""
    global _settings
    if _settings is None:
        _settings = AppSettings.load()
    return _settings


def reload_settings() -> AppSettings:
    """Force reload settings from file."""
    global _settings
    _settings = AppSettings.load()
    return _settings

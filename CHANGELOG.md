# Changelog

All notable changes to DailyWriting will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-04-28

### Added

#### Core Features
- Free writing mode for unstructured daily writing
- AI-powered writing prompts using Google Gemini API
- Writing streak tracking with current and longest streak display
- Calendar view showing writing activity by month
- Session history with full-text search and filtering

#### Statistics Dashboard
- Total sessions, words, and time tracking
- Average words per session and writing speed (WPM)
- Most productive day of week and time of day
- Daily/weekly/monthly word trends
- Daily word goal tracking with progress bar

#### Export & Backup
- Export sessions to Markdown, Plain Text, JSON, or HTML
- Single session and bulk export options
- Manual and automatic backup system
- Backup rotation (7 daily, 4 weekly, 12 monthly)
- Restore from backup with merge support

#### Settings & Configuration
- Customizable daily word goal
- AI model selection (Gemini Flash/Pro)
- Autosave interval configuration
- Font size and line spacing options
- Export format preferences

#### User Interface
- Dark mode interface
- Complete menu bar with keyboard shortcuts
- About dialog and keyboard shortcuts reference
- Loading indicator for AI topic generation
- Confirmation dialogs for destructive actions
- Draft auto-recovery on startup

#### Developer Features
- Comprehensive test suite (115 tests)
- Centralized logging with rotation
- Custom exception hierarchy
- PyInstaller packaging for standalone app
- Build scripts for macOS app bundle

### Technical Details
- Built with Python 3.11+ and PyQt6
- JSON-based local storage
- Layered architecture (core/ui separation)
- Modern Python packaging with pyproject.toml

## [0.1.0] - 2024-11-18

### Added
- Initial prototype
- Basic free writing and AI prompt modes
- Simple calendar view
- Session storage in JSON format
- Streak calculation

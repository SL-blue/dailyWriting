# Changelog

All notable changes to DailyWriting will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-04-30

### Added
- **Light theme**, alongside the existing Dark theme. Switch via Settings → Appearance → Theme; changes apply immediately without restart
- `ui/theme.py` — centralized palette + global stylesheet module. Two palettes (Dark, Light) of ~31 semantic tokens each; `apply_theme(name)` re-styles the running QApplication
- 16 new tests covering palette shape, theme application, fallback behavior, and config round-trip (150 total tests)

### Changed
- All UI files now share a single global stylesheet keyed by object names; nine `_apply_style()` methods removed across `main_window`, `session_view`, `settings_dialog`, `tag_selector_dialog`, `calendar_view`, `history_view`, `stats_view`, `about_dialog`, `shortcuts_dialog`
- `session_view._apply_appearance_settings` reduced to font-only QSS so it no longer overrides theme colors
- Calendar today/completed-day cell colors now come from `current_palette()` so they track the active theme
- Tag selector dialog now follows the app theme — fixed the long-standing visual inconsistency where it was hardcoded light regardless of setting

### Fixed
- Settings dialog Theme picker is now functional (was a cosmetic placeholder showing only "Dark")

---

## [1.3.0] - 2026-04-29

### Added
- **Windows packaging support**: build a standalone `.exe` via `scripts\build_app.bat` and `DailyWriting-windows.spec`
- `scripts/create_icon.py` — cross-platform icon generator (Pillow → `.ico`); replaces the macOS-only `create_icon.sh` for non-macOS environments and works on Windows/Linux out of the box
- README sections for Windows venv activation, Windows API key setup (`setx` and PowerShell), and Windows build instructions
- Settings dialog API-key hint now shows both macOS/Linux and Windows commands

### Notes
- The application's runtime code was already platform-agnostic (uses `pathlib.Path` and `Path.home()` throughout); only the packaging pipeline was macOS-specific. No core code changes were needed
- Windows requires Pillow at build time only (`pip install Pillow`); the build script auto-installs it if missing

---

## [1.2.0] - 2026-04-29

### Added
- **Layered tag system** for AI prompt generation. Four layers (Territory, Emotional Weather, Craft, Seed) over 12 categories, replacing the previous flat tag list
- **Tri-state controls per layer** in the random topic dialog: OFF / RANDOM / PICK, each independently configurable
- **Seed defaults to Random** when no layer state is provided — clicking *Generate* always produces a varied prompt out of the box
- **Anti-repetition mechanism** in every LLM call: rotating "Do not use" list (candles, rain, ticking clocks, music boxes, …) to push the model away from cliché imagery
- 19 new tests covering the layer-based prompt builder (134 total tests)

### Changed
- `Tag` schema replaced: `description` and `elements` (concrete noun lists) removed; `layer` and `directive` added. The old `elements` field caused the model to anchor on repeated nouns
- LLM prompt is now structurally clean — one line per active layer — instead of the previous "writing coach" preamble with example blocks
- `topic_generator.generate_topic()` signature: takes a `layer_state` dict instead of a flat `tag_ids` list
- `tag_selector_dialog.py` redesigned as four layer cards with disclosed pickers in PICK mode

### Removed
- Old categories: `place`, `time`, `event`, `item`, `skill` — superseded by `setting_role`, `time_role`, `situation`, `object_role`, and the Craft layer
- "Writing coach" preamble and per-category example blocks in the LLM instruction

---

## [1.1.0] - 2026-04-29

### Added
- **Dual AI Provider Support**: Choose between Google Gemini and Anthropic Claude for writing prompts
- **Settings Button**: Quick access to settings via ⚙ SETTINGS button in sidebar
- **Automatic Provider Fallback**: If primary AI provider fails, automatically tries the other

### Changed
- Default Gemini model updated to `gemini-2.5-flash` (lower quota usage)
- Default Claude model set to `claude-sonnet-4-5`
- Improved type safety in topic generator with proper None checks

### Fixed
- Pylance type errors in `topic_generator.py`
- Python 3.9 compatibility for type hints in `exceptions.py`

---

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

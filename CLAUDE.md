# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DailyWriting is a production-ready macOS desktop application for daily writing practice. Built with Python 3.13 and PyQt6, it features AI-powered topic generation via Google Gemini, writing streak tracking, comprehensive statistics, search/filter, export/backup, and session management.

## Running the Application

```bash
# From source
python main.py
python main.py --debug  # Enable debug logging

# Build standalone app
./scripts/build_app.sh
open dist/DailyWriting.app
```

Supports two AI providers for topic generation:
- **Gemini**: Set `GOOGLE_API_KEY` environment variable
- **Claude**: Set `ANTHROPIC_API_KEY` environment variable

Falls back to hardcoded prompts if no API keys are configured.

## Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests (115 tests)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov-report=term-missing

# Run a single test file
pytest tests/core/test_statistics.py -v

# Lint
ruff check core/ ui/
```

Logs are written to `~/.dailywriting/logs/dailywriting.log`.

## Architecture

The codebase follows a layered MVC-style architecture:

### Core Layer (`core/`)
Business logic with no UI dependencies:

| Module | Purpose |
|--------|---------|
| `models.py` | `WritingSession` dataclass with metadata, content, metrics |
| `session_manager.py` | Session lifecycle (start → update → finish), auto-save drafts |
| `storage.py` | JSON persistence for sessions in `data/sessions/` |
| `statistics.py` | Comprehensive stats calculations (streaks, averages, trends, goals) |
| `search.py` | Full-text search with filters (date, mode, word count) |
| `export.py` | Export to Markdown, TXT, JSON, HTML |
| `backup.py` | Backup/restore with rotation policy |
| `config.py` | Settings management (`~/.dailywriting/config.json`) |
| `topic_generator.py` | Google Gemini API integration with fallback |
| `prompt_builder.py` | LLM instruction construction from tags |
| `tags.py` | Tag registry (genre, mood, place, time, event, item, skill, form) |
| `streak_days.py` | Consecutive writing day tracking |
| `stats.py` | Legacy streak calculations |
| `utils.py` | Mixed CJK/English word counting |
| `exceptions.py` | Custom exception hierarchy |
| `logging_config.py` | Centralized logging with rotation |

### UI Layer (`ui/`)
PyQt6 widgets and views:

| Module | Purpose |
|--------|---------|
| `main_window.py` | Main container with sidebar, menu bar, stacked views |
| `session_view.py` | Writing editor with timer, title, word count, auto-save |
| `calendar_view.py` | Monthly calendar highlighting writing days |
| `history_view.py` | Session list with search, filter, sort |
| `stats_view.py` | Statistics dashboard with metric cards |
| `settings_dialog.py` | Tabbed preferences dialog |
| `about_dialog.py` | App info dialog |
| `shortcuts_dialog.py` | Keyboard shortcuts reference |
| `tag_selector_dialog.py` | Modal for selecting prompt tags |
| `session_list_dialog.py` | Sessions for a specific date |
| `session_detail_dialog.py` | Full session details with export |

### Data Flow
1. User starts session → SessionManager creates WritingSession
2. User writes → SessionView updates content, auto-saves drafts every 30s
3. User finishes → SessionManager saves to Storage (JSON files)
4. Statistics calculates metrics, StreakDays tracks completion
5. Views refresh to display updated data

## Data Storage

### Sessions (`data/sessions/YYYY-MM-DD/`)
```json
{
  "id": "uuid",
  "title": "session title",
  "session_date": "2025-11-18",
  "mode": "free|random_topic",
  "topic": "AI-generated prompt or null",
  "content": "full writing content",
  "start_time": "ISO timestamp",
  "end_time": "ISO timestamp or null",
  "duration_seconds": 600,
  "char_count": 500,
  "word_count": 100
}
```

### Settings (`~/.dailywriting/config.json`)
```json
{
  "ai": {
    "provider": "gemini",
    "gemini_model": "gemini-2.5-pro",
    "claude_model": "claude-sonnet-4-20250514",
    "retry_count": 3
  },
  "writing": {"default_mode": "free", "autosave_interval": 30, "daily_word_goal": 500},
  "export": {"default_format": "markdown", "include_metadata": true},
  "appearance": {"font_size": 18, "line_spacing": 1.5}
}
```

### Other Storage
- `data/streak_days.json` - List of completion dates
- `~/.dailywriting/drafts/` - Auto-saved session drafts
- `~/.dailywriting/backups/` - Backup archives
- `~/.dailywriting/logs/` - Application logs

## Key Implementation Notes

- **CJK Support**: `utils.mixed_word_count()` handles mixed CJK/English using Unicode ranges
- **AI Fallback**: TopicGenerator retries on 503 errors, falls back to local prompts
- **Tag System**: Tags inspire prompt generation without appearing explicitly
- **Auto-Recovery**: Abandoned drafts are detected on startup and offered for recovery
- **Statistics**: Full stats including streaks, averages, productivity insights, goal tracking
- **Search**: Real-time filtering with query, mode, date range, word count filters

## Testing

Tests are organized by layer:
- `tests/core/` - Business logic tests (no Qt required)
- `tests/conftest.py` - Shared fixtures

Current coverage: 115 tests passing.

## Building

```bash
# Create standalone macOS app
./scripts/build_app.sh

# Create custom icon
./scripts/create_icon.sh path/to/1024x1024.png
```

Output: `dist/DailyWriting.app` (~87MB standalone)

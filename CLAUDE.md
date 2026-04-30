# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DailyWriting is a production-ready macOS desktop application for daily writing practice. Built with Python 3.9+ and PyQt6, it features AI-powered topic generation via Google Gemini or Anthropic Claude (with automatic fallback), writing streak tracking, comprehensive statistics, search/filter, export/backup, and session management.

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

# Run tests (134 tests)
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
| `topic_generator.py` | Dual AI provider support (Gemini/Claude) with automatic fallback |
| `prompt_builder.py` | Builds the LLM instruction from per-layer state (Off / Random / Specified) |
| `tags.py` | Layered tag registry: 4 layers (territory, emotional_weather, craft, seed) over 12 categories |
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
    "gemini_model": "gemini-2.5-flash",
    "claude_model": "claude-sonnet-4-5",
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
- **AI Fallback**: TopicGenerator supports dual providers (Gemini/Claude), retries on errors, falls back between providers, then to local prompts
- **Tag System**: Four-layer model (Territory, Emotional Weather, Craft, Seed). Each layer is independently Off / Random / Specified. Random selection happens at *generation time*, so re-rolling produces variety. Seed defaults to Random when no layer state is provided. See `TAG_SYSTEM_SPEC.md` for the full design contract.
- **Auto-Recovery**: Abandoned drafts are detected on startup and offered for recovery
- **Statistics**: Full stats including streaks, averages, productivity insights, goal tracking
- **Search**: Real-time filtering with query, mode, date range, word count filters

## Tag System

The prompt system is layered — see `TAG_SYSTEM_SPEC.md` for the full design contract. A summary of what code agents need to know:

### Layers and categories

| Layer | Categories |
|---|---|
| `territory` | `genre`, `register` |
| `emotional_weather` | `mood`, `tension` |
| `craft` | `perspective`, `temporal_stance`, `structural_move`, `form` |
| `seed` | `situation`, `object_role`, `setting_role`, `time_role` |

Each `Tag` has: `id`, `category`, `layer`, `label` (user-facing), `directive` (the phrase injected into the prompt). Tags do **not** carry concrete noun lists — that was the old system and produced repetitive output.

### LayerState — the contract between UI and prompt builder

`prompt_builder.build_topic_instruction(layer_state)` and `topic_generator.generate_topic(layer_state)` both consume the same dict shape:

```python
{
    "territory":         {"state": "off"},
    "emotional_weather": {"state": "random"},
    "craft":             {"state": "specified", "tag_ids": ["perspective_second", "form_paragraph"]},
    "seed":              {"state": "random"},
}
```

- `state` is one of `"off"`, `"random"`, `"specified"`.
- `tag_ids` is only read when `state == "specified"`.
- If `layer_state` is `None` or omits a layer, `seed` defaults to `"random"` and other layers default to `"off"`.

### Random selection rules

- For `territory`, `emotional_weather`, `craft` in RANDOM: pick one tag from one randomly-chosen category in the layer.
- For `seed` in RANDOM: pick from `situation` OR one of the role categories — never both. A situation tag alone is usually enough to anchor a scene.
- The form tag (from Craft) drives the closing instruction (`Write exactly one sentence.` / `Write a short paragraph (2–4 sentences).` / `Write exactly two sentences.` / default `Write one or two sentences.`).
- Each generated prompt always includes `Invent all specifics. Avoid the most obvious imagery for this combination.` plus a rotating `Do not use: …` list of 4 overused defaults.

### Where the layers come together

| File | Role |
|---|---|
| `core/tags.py` | `TAG_REGISTRY`, `LAYER_CATEGORIES`, `LAYER_LABELS`, helpers |
| `core/prompt_builder.py` | Resolves layer state → list of selected tags → final instruction string |
| `core/topic_generator.py` | Calls `build_topic_instruction(layer_state)` and ships it to Gemini/Claude |
| `ui/tag_selector_dialog.py` | Four `LayerCard` widgets with Off/Random/Pick tri-state and disclosed picker; emits `selected_layer_state()` |
| `tests/core/test_prompt_builder.py` | Verifies defaults, off/random/specified per layer, form-tag closings, anti-repetition |

### Adding new tags

1. Add a `Tag(...)` entry to `_RAW_TAGS` in `core/tags.py` under the right layer/category section. Use a unique `id` and a short, label-style `directive`.
2. The dialog auto-discovers new tags via `tags_in_category()` — no UI change needed unless you add a new *category*.
3. New categories must be registered in `LAYER_CATEGORIES` (and the dialog's `_CATEGORY_LABELS` map for a human label).

## Testing

Tests are organized by layer:
- `tests/core/` - Business logic tests (no Qt required)
- `tests/conftest.py` - Shared fixtures

Current coverage: 134 tests passing.

## Building

```bash
# Create standalone macOS app
./scripts/build_app.sh

# Create custom icon
./scripts/create_icon.sh path/to/1024x1024.png
```

Output: `dist/DailyWriting.app` (~87MB standalone)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DailyWriting is a macOS desktop application for daily writing practice. Built with Python 3.13 and PyQt6, it features AI-powered topic generation via Google Gemini, writing streak tracking, and session management.

## Running the Application

```bash
python main.py
```

Requires `GOOGLE_API_KEY` environment variable for AI topic generation. Falls back to hardcoded prompts if missing.

## Architecture

The codebase follows a layered MVC-style architecture:

### Core Layer (`core/`)
- **models.py** - `WritingSession` dataclass containing session metadata, content, and metrics
- **session_manager.py** - Manages active session lifecycle (start → update → finish)
- **storage.py** - JSON persistence for sessions (`data/sessions/`) and streak tracking
- **topic_generator.py** - Google Gemini API integration for AI-generated writing prompts
- **prompt_builder.py** - Constructs LLM instructions from selected tags
- **tags.py** - Tag registry organized by category (genre, mood, place, time, event, item, skill, form)
- **streak_days.py** - Tracks consecutive writing days
- **stats.py** - Calculates current streak, longest streak, total days
- **utils.py** - Mixed CJK/English word counting

### UI Layer (`ui/`)
- **main_window.py** - Application container with sidebar navigation and stacked views
- **session_view.py** - Active writing editor with timer, title, word count
- **calendar_view.py** - Calendar widget highlighting writing days
- **history_view.py** - Scrollable list of past sessions
- **tag_selector_dialog.py** - Modal for selecting writing prompt tags
- **session_list_dialog.py** - Dialog listing sessions for a specific date
- **session_detail_dialog.py** - Modal showing full session details

### Data Flow
1. User starts session → SessionManager creates WritingSession
2. User writes → SessionView updates content in real-time
3. User finishes → SessionManager saves to Storage (JSON files)
4. StreakDays tracks completion, Stats computes streaks
5. CalendarView displays highlighted writing days

## Data Storage

Sessions stored as JSON in `data/sessions/` with structure:
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
  "duration_seconds": 12,
  "char_count": 12,
  "word_count": 2
}
```

Streak days tracked in `data/streak_days.json` as a list of date strings.

## Key Implementation Notes

- **CJK Support**: `utils.mixed_word_count()` handles mixed CJK/English text using Unicode range detection (0x4E00-0x9FFF)
- **AI Fallback**: TopicGenerator includes retry logic for 503 errors and fallback prompts when API unavailable
- **Tag System**: Tags serve as invisible inspirations for prompt generation, not explicit requirements in the output

# core/streak_days.py

import json
from pathlib import Path
from datetime import date, timedelta
from typing import Set, List

from .storage import DATA_DIR, load_sessions_for_date

STREAK_FILE = DATA_DIR / "streak_days.json"


def load_completed_days() -> Set[date]:
    """Load the set of days that count as completed for streak."""
    if not STREAK_FILE.exists():
        return set()
    try:
        with STREAK_FILE.open("r", encoding="utf-8") as f:
            raw: List[str] = json.load(f)
        return {date.fromisoformat(d) for d in raw}
    except Exception:
        return set()


def save_completed_days(days: Set[date]) -> None:
    """Save the set of completed streak days."""
    raw = sorted(d.isoformat() for d in days)
    STREAK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STREAK_FILE.open("w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)


def mark_day_completed(d: date) -> None:
    """Mark this date as a completed writing day."""
    days = load_completed_days()
    if d not in days:
        days.add(d)
        save_completed_days(days)


def maybe_unmark_today_if_empty(d: date) -> None:
    """
    Remove TODAY from completed days only if:
      - the deleted session is from today, AND
      - now there are NO sessions remaining today.

    Deletions on old days do NOT remove streak history.
    """
    today = date.today()

    # Only care about today
    if d != today:
        return

    # If there are still sessions today, do nothing
    if load_sessions_for_date(today):
        return

    # Otherwise remove today from streak log
    days = load_completed_days()
    if today in days:
        days.remove(today)
        save_completed_days(days)


def compute_streaks_from_days(days: Set[date]):
    """Compute streak values from a set of completed streak days."""
    if not days:
        return 0, 0, 0

    sorted_days = sorted(days)
    day_set = set(sorted_days)

    today = date.today()
    current = 0

    # current streak
    d = today
    while d in day_set:
        current += 1
        d = d - timedelta(days=1)

    # longest streak
    longest = 0
    for day in sorted_days:
        if (day - timedelta(days=1)) not in day_set:
            length = 1
            nxt = day + timedelta(days=1)
            while nxt in day_set:
                length += 1
                nxt = nxt + timedelta(days=1)
            longest = max(longest, length)

    total = len(day_set)
    return current, longest, total

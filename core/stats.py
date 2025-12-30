"""
Compute writing streaks from writing sessions and return stats.
"""

from datetime import date, timedelta
from typing import Iterable, Set

from .models import WritingSession


def _completed_days_from_sessions(sessions: Iterable[WritingSession]) -> Set[date]:
    """
    Return the set of dates that have at least one completed session.
    For now: every saved session counts, no min chars/minutes.

    Args:
        sessions: Iterable of WritingSession objects
    Returns:
        Set of dates with at least one session
    """
    return {s.session_date for s in sessions}


def compute_streaks(sessions: Iterable[WritingSession]):
    """
    Given all sessions, compute:
      - current_streak: number of consecutive days up to today with writing
      - longest_streak: longest such run ever
      - total_days: total distinct days with sessions
    Args:
        sessions: Iterable of WritingSession objects
    Returns:
        Tuple of (current_streak, longest_streak, total_days)
    """

    completed_days = sorted(_completed_days_from_sessions(sessions))
    if not completed_days:
        return 0, 0, 0

    completed_set = set(completed_days)

    # --- current streak ---
    today = date.today()
    current_streak = 0
    d = today
    while d in completed_set:
        current_streak += 1
        d = d - timedelta(days=1)

    # --- longest streak ---
    longest_streak = 0
    # iterate through all days, grow streaks whenever they start
    for day in completed_days:
        # if the previous day isn't completed, this is a potential streak start
        if (day - timedelta(days=1)) not in completed_set:
            length = 1
            next_day = day + timedelta(days=1)
            while next_day in completed_set:
                length += 1
                next_day = next_day + timedelta(days=1)
            longest_streak = max(longest_streak, length)

    total_days = len(completed_set)
    return current_streak, longest_streak, total_days

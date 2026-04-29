"""
Tests for core/stats.py - streak calculation logic.
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from core.stats import compute_streaks, _completed_days_from_sessions
from core.models import WritingSession


def make_session(session_date: date) -> WritingSession:
    """Helper to create a minimal session for a given date."""
    return WritingSession(
        id=f"session-{session_date.isoformat()}",
        title="Test",
        session_date=session_date,
        mode="free",
        topic=None,
        content="test",
        start_time=datetime.combine(session_date, datetime.min.time()),
        end_time=None,
        duration_seconds=0,
        char_count=4,
        word_count=1,
    )


class TestCompletedDaysFromSessions:
    """Tests for _completed_days_from_sessions helper."""

    def test_empty_sessions(self):
        assert _completed_days_from_sessions([]) == set()

    def test_single_session(self):
        sessions = [make_session(date(2025, 1, 15))]
        assert _completed_days_from_sessions(sessions) == {date(2025, 1, 15)}

    def test_multiple_sessions_same_day(self):
        sessions = [
            make_session(date(2025, 1, 15)),
            make_session(date(2025, 1, 15)),
        ]
        # Should deduplicate to single date
        assert _completed_days_from_sessions(sessions) == {date(2025, 1, 15)}

    def test_multiple_different_days(self):
        sessions = [
            make_session(date(2025, 1, 15)),
            make_session(date(2025, 1, 16)),
            make_session(date(2025, 1, 17)),
        ]
        assert _completed_days_from_sessions(sessions) == {
            date(2025, 1, 15),
            date(2025, 1, 16),
            date(2025, 1, 17),
        }


class TestComputeStreaks:
    """Tests for compute_streaks function."""

    def test_no_sessions(self):
        current, longest, total = compute_streaks([])
        assert current == 0
        assert longest == 0
        assert total == 0

    def test_single_session_today(self):
        today = date.today()
        sessions = [make_session(today)]

        with patch("core.stats.date") as mock_date:
            mock_date.today.return_value = today
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

            current, longest, total = compute_streaks(sessions)

        assert current == 1
        assert longest == 1
        assert total == 1

    def test_single_session_yesterday(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        sessions = [make_session(yesterday)]

        current, longest, total = compute_streaks(sessions)

        # Yesterday without today breaks the streak
        assert current == 0
        assert longest == 1
        assert total == 1

    def test_consecutive_days_including_today(self):
        today = date.today()
        sessions = [
            make_session(today - timedelta(days=2)),
            make_session(today - timedelta(days=1)),
            make_session(today),
        ]

        current, longest, total = compute_streaks(sessions)

        assert current == 3
        assert longest == 3
        assert total == 3

    def test_gap_in_streak(self):
        today = date.today()
        sessions = [
            make_session(today - timedelta(days=5)),
            make_session(today - timedelta(days=4)),
            # Gap on day -3
            make_session(today - timedelta(days=2)),
            make_session(today - timedelta(days=1)),
            make_session(today),
        ]

        current, longest, total = compute_streaks(sessions)

        assert current == 3  # Last 3 days
        assert longest == 3  # Both streaks are length 2 and 3
        assert total == 5

    def test_longer_past_streak(self):
        today = date.today()
        sessions = [
            # Old streak of 5 days
            make_session(today - timedelta(days=20)),
            make_session(today - timedelta(days=19)),
            make_session(today - timedelta(days=18)),
            make_session(today - timedelta(days=17)),
            make_session(today - timedelta(days=16)),
            # Gap
            # Current streak of 2 days
            make_session(today - timedelta(days=1)),
            make_session(today),
        ]

        current, longest, total = compute_streaks(sessions)

        assert current == 2
        assert longest == 5
        assert total == 7

    def test_multiple_sessions_same_day(self):
        today = date.today()
        sessions = [
            make_session(today),
            make_session(today),  # Same day
            make_session(today),  # Same day again
        ]

        current, longest, total = compute_streaks(sessions)

        assert current == 1
        assert longest == 1
        assert total == 1  # Only 1 unique day

    def test_non_consecutive_days(self):
        today = date.today()
        sessions = [
            make_session(today - timedelta(days=10)),
            make_session(today - timedelta(days=5)),
            make_session(today - timedelta(days=2)),
        ]

        current, longest, total = compute_streaks(sessions)

        assert current == 0  # No session today or yesterday continuing
        assert longest == 1  # Each day is its own streak of 1
        assert total == 3

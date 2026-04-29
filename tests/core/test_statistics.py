"""
Tests for core/statistics.py - comprehensive statistics calculations.
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from core.statistics import (
    StatisticsCalculator,
    calculate_statistics,
    format_duration,
    format_hour,
    CoreStats,
    AverageStats,
    StreakStats,
)
from core.models import WritingSession


def make_session(
    id: str = "test",
    session_date: date = None,
    word_count: int = 100,
    char_count: int = 500,
    duration_seconds: int = 600,
    mode: str = "free",
    start_hour: int = 10,
) -> WritingSession:
    """Helper to create test sessions."""
    if session_date is None:
        session_date = date.today()

    return WritingSession(
        id=id,
        title=f"Session {id}",
        session_date=session_date,
        mode=mode,
        topic=None,
        content="Test content",
        start_time=datetime.combine(session_date, datetime.min.time().replace(hour=start_hour)),
        end_time=datetime.combine(session_date, datetime.min.time().replace(hour=start_hour, minute=10)),
        duration_seconds=duration_seconds,
        char_count=char_count,
        word_count=word_count,
    )


class TestCoreStats:
    """Tests for core statistics calculations."""

    def test_empty_sessions(self):
        calc = StatisticsCalculator([])
        stats = calc.calculate_all()

        assert stats.core.total_sessions == 0
        assert stats.core.total_words == 0
        assert stats.core.total_duration_seconds == 0

    def test_single_session(self):
        sessions = [make_session(word_count=100, duration_seconds=600)]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.core.total_sessions == 1
        assert stats.core.total_words == 100
        assert stats.core.total_duration_seconds == 600
        assert stats.core.unique_days == 1

    def test_multiple_sessions(self):
        today = date.today()
        sessions = [
            make_session(id="1", session_date=today, word_count=100),
            make_session(id="2", session_date=today, word_count=200),
            make_session(id="3", session_date=today - timedelta(days=1), word_count=150),
        ]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.core.total_sessions == 3
        assert stats.core.total_words == 450
        assert stats.core.unique_days == 2


class TestAverageStats:
    """Tests for average statistics calculations."""

    def test_averages(self):
        sessions = [
            make_session(id="1", word_count=100, duration_seconds=600),
            make_session(id="2", word_count=200, duration_seconds=1200),
        ]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.averages.words_per_session == 150.0
        assert stats.averages.duration_per_session_minutes == 15.0

    def test_words_per_minute(self):
        sessions = [
            make_session(word_count=120, duration_seconds=60),  # 120 wpm
        ]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.averages.words_per_minute == 120.0


class TestStreakStats:
    """Tests for streak calculations."""

    def test_no_current_streak(self):
        # Session from a week ago
        old_date = date.today() - timedelta(days=7)
        sessions = [make_session(session_date=old_date)]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.streaks.current_streak == 0
        assert stats.streaks.longest_streak == 1

    def test_current_streak(self):
        today = date.today()
        sessions = [
            make_session(id="1", session_date=today),
            make_session(id="2", session_date=today - timedelta(days=1)),
            make_session(id="3", session_date=today - timedelta(days=2)),
        ]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.streaks.current_streak == 3
        assert stats.streaks.longest_streak == 3

    def test_longest_streak_in_past(self):
        today = date.today()
        sessions = [
            # Current streak of 1
            make_session(id="1", session_date=today),
            # Gap
            # Old streak of 5
            make_session(id="2", session_date=today - timedelta(days=10)),
            make_session(id="3", session_date=today - timedelta(days=11)),
            make_session(id="4", session_date=today - timedelta(days=12)),
            make_session(id="5", session_date=today - timedelta(days=13)),
            make_session(id="6", session_date=today - timedelta(days=14)),
        ]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.streaks.current_streak == 1
        assert stats.streaks.longest_streak == 5


class TestProductivityStats:
    """Tests for productivity insights."""

    def test_most_productive_weekday(self):
        # Create sessions on Monday with most words
        monday = date.today() - timedelta(days=date.today().weekday())
        tuesday = monday + timedelta(days=1)

        sessions = [
            make_session(id="1", session_date=monday, word_count=500),
            make_session(id="2", session_date=tuesday, word_count=100),
        ]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.productivity.most_productive_weekday == "Monday"
        assert stats.productivity.most_productive_weekday_words == 500

    def test_most_productive_hour(self):
        today = date.today()
        sessions = [
            make_session(id="1", session_date=today, start_hour=9),
            make_session(id="2", session_date=today, start_hour=9),
            make_session(id="3", session_date=today, start_hour=14),
        ]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.productivity.most_productive_hour == 9
        assert stats.productivity.most_productive_hour_sessions == 2

    def test_best_session(self):
        today = date.today()
        sessions = [
            make_session(id="1", session_date=today, word_count=100),
            make_session(id="2", session_date=today, word_count=500),
            make_session(id="3", session_date=today, word_count=200),
        ]
        calc = StatisticsCalculator(sessions)
        stats = calc.calculate_all()

        assert stats.productivity.best_session_words == 500


class TestGoalStats:
    """Tests for goal tracking."""

    def test_no_goal(self):
        sessions = [make_session(word_count=100)]
        calc = StatisticsCalculator(sessions, daily_goal=0)
        stats = calc.calculate_all()

        assert stats.goals.daily_goal == 0
        assert stats.goals.today_progress_percent == 0.0

    def test_goal_progress(self):
        today = date.today()
        sessions = [
            make_session(id="1", session_date=today, word_count=250),
        ]
        calc = StatisticsCalculator(sessions, daily_goal=500)
        stats = calc.calculate_all()

        assert stats.goals.daily_goal == 500
        assert stats.goals.today_words == 250
        assert stats.goals.today_progress_percent == 50.0

    def test_goal_exceeded(self):
        today = date.today()
        sessions = [
            make_session(id="1", session_date=today, word_count=600),
        ]
        calc = StatisticsCalculator(sessions, daily_goal=500)
        stats = calc.calculate_all()

        # Progress capped at 100%
        assert stats.goals.today_progress_percent == 100.0

    def test_goal_streak(self):
        today = date.today()
        sessions = [
            make_session(id="1", session_date=today, word_count=600),
            make_session(id="2", session_date=today - timedelta(days=1), word_count=550),
            make_session(id="3", session_date=today - timedelta(days=2), word_count=520),
        ]
        calc = StatisticsCalculator(sessions, daily_goal=500)
        stats = calc.calculate_all()

        assert stats.goals.goal_streak == 3


class TestConvenienceFunction:
    """Tests for the calculate_statistics convenience function."""

    def test_calculate_statistics(self):
        sessions = [make_session(word_count=100)]
        stats = calculate_statistics(sessions, daily_goal=200)

        assert stats.core.total_words == 100
        assert stats.goals.daily_goal == 200


class TestFormatFunctions:
    """Tests for formatting helper functions."""

    def test_format_duration_seconds(self):
        assert format_duration(30) == "30s"

    def test_format_duration_minutes(self):
        assert format_duration(90) == "1m"
        assert format_duration(600) == "10m"

    def test_format_duration_hours(self):
        assert format_duration(3660) == "1h 1m"
        assert format_duration(7200) == "2h 0m"

    def test_format_hour_am(self):
        assert format_hour(0) == "12 AM"
        assert format_hour(9) == "9 AM"
        assert format_hour(11) == "11 AM"

    def test_format_hour_pm(self):
        assert format_hour(12) == "12 PM"
        assert format_hour(13) == "1 PM"
        assert format_hour(23) == "11 PM"

"""
Comprehensive statistics calculations for writing sessions.

Provides:
- Core metrics (total sessions, words, time)
- Averages (words per session, duration, writing speed)
- Streaks and consistency
- Productivity insights (best day, best time)
- Trends (weekly, monthly)
- Goal tracking
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple

from .models import WritingSession
from .logging_config import get_logger

logger = get_logger("statistics")


@dataclass
class CoreStats:
    """Basic aggregate statistics."""
    total_sessions: int = 0
    total_words: int = 0
    total_characters: int = 0
    total_duration_seconds: int = 0
    unique_days: int = 0


@dataclass
class AverageStats:
    """Average/derived statistics."""
    words_per_session: float = 0.0
    chars_per_session: float = 0.0
    duration_per_session_minutes: float = 0.0
    words_per_minute: float = 0.0
    sessions_per_week: float = 0.0


@dataclass
class StreakStats:
    """Streak-related statistics."""
    current_streak: int = 0
    longest_streak: int = 0
    current_streak_start: Optional[date] = None
    longest_streak_start: Optional[date] = None
    longest_streak_end: Optional[date] = None


@dataclass
class ProductivityStats:
    """Productivity insights."""
    most_productive_weekday: Optional[str] = None  # "Monday", "Tuesday", etc.
    most_productive_weekday_words: int = 0
    most_productive_hour: Optional[int] = None  # 0-23
    most_productive_hour_sessions: int = 0
    best_session_words: int = 0
    best_session_date: Optional[date] = None


@dataclass
class TrendStats:
    """Trend data for charts."""
    # Words per day for last 30 days
    daily_words: Dict[date, int] = None
    # Words per week for last 12 weeks
    weekly_words: Dict[str, int] = None  # "2025-W01" format
    # Words per month for last 12 months
    monthly_words: Dict[str, int] = None  # "2025-01" format

    def __post_init__(self):
        if self.daily_words is None:
            self.daily_words = {}
        if self.weekly_words is None:
            self.weekly_words = {}
        if self.monthly_words is None:
            self.monthly_words = {}


@dataclass
class GoalStats:
    """Goal tracking statistics."""
    daily_goal: int = 0
    today_words: int = 0
    today_progress_percent: float = 0.0
    days_goal_met_this_week: int = 0
    days_goal_met_this_month: int = 0
    goal_streak: int = 0  # Consecutive days meeting goal


@dataclass
class WritingStatistics:
    """Complete statistics container."""
    core: CoreStats
    averages: AverageStats
    streaks: StreakStats
    productivity: ProductivityStats
    trends: TrendStats
    goals: GoalStats


class StatisticsCalculator:
    """Calculate comprehensive writing statistics."""

    WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def __init__(self, sessions: List[WritingSession], daily_goal: int = 0):
        """
        Initialize calculator with sessions.

        Args:
            sessions: List of WritingSession objects.
            daily_goal: Daily word goal (0 = no goal).
        """
        self.sessions = sessions
        self.daily_goal = daily_goal
        self._today = date.today()

    def calculate_all(self) -> WritingStatistics:
        """Calculate all statistics."""
        return WritingStatistics(
            core=self._calculate_core(),
            averages=self._calculate_averages(),
            streaks=self._calculate_streaks(),
            productivity=self._calculate_productivity(),
            trends=self._calculate_trends(),
            goals=self._calculate_goals(),
        )

    def _calculate_core(self) -> CoreStats:
        """Calculate core aggregate statistics."""
        if not self.sessions:
            return CoreStats()

        total_words = sum(s.word_count for s in self.sessions)
        total_chars = sum(s.char_count for s in self.sessions)
        total_duration = sum(s.duration_seconds for s in self.sessions)
        unique_days = len(set(s.session_date for s in self.sessions))

        return CoreStats(
            total_sessions=len(self.sessions),
            total_words=total_words,
            total_characters=total_chars,
            total_duration_seconds=total_duration,
            unique_days=unique_days,
        )

    def _calculate_averages(self) -> AverageStats:
        """Calculate average statistics."""
        if not self.sessions:
            return AverageStats()

        core = self._calculate_core()
        n = core.total_sessions

        words_per_session = core.total_words / n
        chars_per_session = core.total_characters / n
        duration_minutes = (core.total_duration_seconds / 60) / n

        # Words per minute (avoid division by zero)
        total_minutes = core.total_duration_seconds / 60
        words_per_minute = core.total_words / total_minutes if total_minutes > 0 else 0

        # Sessions per week (based on date range)
        if core.unique_days > 1:
            dates = sorted(s.session_date for s in self.sessions)
            days_span = (dates[-1] - dates[0]).days + 1
            weeks_span = max(1, days_span / 7)
            sessions_per_week = n / weeks_span
        else:
            sessions_per_week = n

        return AverageStats(
            words_per_session=round(words_per_session, 1),
            chars_per_session=round(chars_per_session, 1),
            duration_per_session_minutes=round(duration_minutes, 1),
            words_per_minute=round(words_per_minute, 1),
            sessions_per_week=round(sessions_per_week, 1),
        )

    def _calculate_streaks(self) -> StreakStats:
        """Calculate streak statistics."""
        if not self.sessions:
            return StreakStats()

        # Get unique dates with sessions
        session_dates = sorted(set(s.session_date for s in self.sessions))

        if not session_dates:
            return StreakStats()

        # Current streak (counting back from today)
        current_streak = 0
        current_streak_start = None
        check_date = self._today

        while check_date in session_dates:
            current_streak += 1
            current_streak_start = check_date
            check_date -= timedelta(days=1)

        # If no session today, check if yesterday continues a streak
        if current_streak == 0:
            check_date = self._today - timedelta(days=1)
            while check_date in session_dates:
                # Don't count as current streak if gap exists
                check_date -= timedelta(days=1)

        # Find longest streak
        longest_streak = 0
        longest_start = None
        longest_end = None

        i = 0
        while i < len(session_dates):
            streak_start = session_dates[i]
            streak_length = 1

            while (i + 1 < len(session_dates) and
                   session_dates[i + 1] == session_dates[i] + timedelta(days=1)):
                streak_length += 1
                i += 1

            if streak_length > longest_streak:
                longest_streak = streak_length
                longest_start = streak_start
                longest_end = session_dates[i]

            i += 1

        return StreakStats(
            current_streak=current_streak,
            longest_streak=longest_streak,
            current_streak_start=current_streak_start,
            longest_streak_start=longest_start,
            longest_streak_end=longest_end,
        )

    def _calculate_productivity(self) -> ProductivityStats:
        """Calculate productivity insights."""
        if not self.sessions:
            return ProductivityStats()

        # Words by weekday
        weekday_words: Dict[int, int] = defaultdict(int)
        for s in self.sessions:
            weekday_words[s.session_date.weekday()] += s.word_count

        if weekday_words:
            best_weekday = max(weekday_words, key=weekday_words.get)
            best_weekday_name = self.WEEKDAY_NAMES[best_weekday]
            best_weekday_words = weekday_words[best_weekday]
        else:
            best_weekday_name = None
            best_weekday_words = 0

        # Sessions by hour
        hour_sessions: Dict[int, int] = defaultdict(int)
        for s in self.sessions:
            if s.start_time:
                hour_sessions[s.start_time.hour] += 1

        if hour_sessions:
            best_hour = max(hour_sessions, key=hour_sessions.get)
            best_hour_sessions = hour_sessions[best_hour]
        else:
            best_hour = None
            best_hour_sessions = 0

        # Best single session
        best_session = max(self.sessions, key=lambda s: s.word_count)

        return ProductivityStats(
            most_productive_weekday=best_weekday_name,
            most_productive_weekday_words=best_weekday_words,
            most_productive_hour=best_hour,
            most_productive_hour_sessions=best_hour_sessions,
            best_session_words=best_session.word_count,
            best_session_date=best_session.session_date,
        )

    def _calculate_trends(self) -> TrendStats:
        """Calculate trend data for visualization."""
        trends = TrendStats()

        if not self.sessions:
            return trends

        # Daily words (last 30 days)
        thirty_days_ago = self._today - timedelta(days=30)
        for s in self.sessions:
            if s.session_date >= thirty_days_ago:
                if s.session_date not in trends.daily_words:
                    trends.daily_words[s.session_date] = 0
                trends.daily_words[s.session_date] += s.word_count

        # Weekly words (last 12 weeks)
        twelve_weeks_ago = self._today - timedelta(weeks=12)
        for s in self.sessions:
            if s.session_date >= twelve_weeks_ago:
                week_key = s.session_date.strftime("%Y-W%W")
                if week_key not in trends.weekly_words:
                    trends.weekly_words[week_key] = 0
                trends.weekly_words[week_key] += s.word_count

        # Monthly words (last 12 months)
        twelve_months_ago = self._today.replace(year=self._today.year - 1)
        for s in self.sessions:
            if s.session_date >= twelve_months_ago:
                month_key = s.session_date.strftime("%Y-%m")
                if month_key not in trends.monthly_words:
                    trends.monthly_words[month_key] = 0
                trends.monthly_words[month_key] += s.word_count

        return trends

    def _calculate_goals(self) -> GoalStats:
        """Calculate goal-related statistics."""
        if self.daily_goal <= 0:
            return GoalStats()

        # Today's words
        today_words = sum(
            s.word_count for s in self.sessions
            if s.session_date == self._today
        )
        today_progress = min(100.0, (today_words / self.daily_goal) * 100)

        # Days meeting goal this week
        week_start = self._today - timedelta(days=self._today.weekday())
        daily_totals = defaultdict(int)
        for s in self.sessions:
            if s.session_date >= week_start:
                daily_totals[s.session_date] += s.word_count

        days_met_week = sum(1 for words in daily_totals.values() if words >= self.daily_goal)

        # Days meeting goal this month
        month_start = self._today.replace(day=1)
        monthly_totals = defaultdict(int)
        for s in self.sessions:
            if s.session_date >= month_start:
                monthly_totals[s.session_date] += s.word_count

        days_met_month = sum(1 for words in monthly_totals.values() if words >= self.daily_goal)

        # Goal streak (consecutive days meeting goal)
        all_daily_totals = defaultdict(int)
        for s in self.sessions:
            all_daily_totals[s.session_date] += s.word_count

        goal_streak = 0
        check_date = self._today
        while all_daily_totals.get(check_date, 0) >= self.daily_goal:
            goal_streak += 1
            check_date -= timedelta(days=1)

        return GoalStats(
            daily_goal=self.daily_goal,
            today_words=today_words,
            today_progress_percent=round(today_progress, 1),
            days_goal_met_this_week=days_met_week,
            days_goal_met_this_month=days_met_month,
            goal_streak=goal_streak,
        )


def calculate_statistics(
    sessions: List[WritingSession],
    daily_goal: int = 0
) -> WritingStatistics:
    """
    Convenience function to calculate all statistics.

    Args:
        sessions: List of WritingSession objects.
        daily_goal: Daily word goal (0 = no goal).

    Returns:
        WritingStatistics with all calculated metrics.
    """
    calculator = StatisticsCalculator(sessions, daily_goal)
    return calculator.calculate_all()


def format_duration(seconds: int) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_hour(hour: int) -> str:
    """Format hour (0-23) as readable time."""
    if hour == 0:
        return "12 AM"
    elif hour < 12:
        return f"{hour} AM"
    elif hour == 12:
        return "12 PM"
    else:
        return f"{hour - 12} PM"

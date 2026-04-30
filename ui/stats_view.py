# ui/stats_view.py

"""
Statistics dashboard view showing writing metrics and progress.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QScrollArea,
    QProgressBar,
)
from PyQt6.QtCore import Qt

from core.storage import load_all_sessions
from core.statistics import (
    calculate_statistics,
    format_duration,
    format_hour,
    WritingStatistics,
)
from core.config import get_settings
from core.logging_config import get_logger

logger = get_logger("stats_view")


class StatCard(QFrame):
    """A card displaying a single statistic."""

    def __init__(self, title: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("StatCardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("StatCardValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("StatCardSubtitle")
            layout.addWidget(subtitle_label)

    def update_value(self, value: str, subtitle: str = ""):
        """Update the displayed value."""
        value_label = self.findChild(QLabel, "StatCardValue")
        if value_label:
            value_label.setText(value)


class GoalProgressCard(QFrame):
    """A card showing goal progress with a progress bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GoalCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title_label = QLabel("TODAY'S GOAL")
        title_label.setObjectName("StatCardTitle")
        layout.addWidget(title_label)

        self.words_label = QLabel("0 / 0 words")
        self.words_label.setObjectName("GoalWordsLabel")
        layout.addWidget(self.words_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("GoalProgressBar")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.streak_label = QLabel("")
        self.streak_label.setObjectName("GoalStreakLabel")
        layout.addWidget(self.streak_label)

    def update_progress(self, current: int, goal: int, streak: int = 0):
        """Update the goal progress display."""
        self.words_label.setText(f"{current:,} / {goal:,} words")

        percent = min(100, int((current / goal) * 100)) if goal > 0 else 0
        self.progress_bar.setValue(percent)

        if streak > 0:
            self.streak_label.setText(f"Goal met {streak} days in a row!")
        else:
            self.streak_label.setText("")


class StatsView(QWidget):
    """Statistics dashboard view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatsView")

        self._build_ui()

    def _build_ui(self):
        """Build the dashboard UI."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setSpacing(24)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("StatsScrollArea")

        content = QWidget()
        content.setObjectName("StatsContent")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(24)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        # Build sections
        self._build_overview_section()
        self._build_averages_section()
        self._build_streaks_section()
        self._build_productivity_section()
        self._build_goal_section()

        self.content_layout.addStretch()

    def _build_overview_section(self):
        """Build the overview stats section."""
        section = self._create_section("OVERVIEW")

        grid = QGridLayout()
        grid.setSpacing(16)

        self.total_sessions_card = StatCard("TOTAL SESSIONS", "0")
        self.total_words_card = StatCard("TOTAL WORDS", "0")
        self.total_time_card = StatCard("TOTAL TIME", "0m")
        self.unique_days_card = StatCard("WRITING DAYS", "0")

        grid.addWidget(self.total_sessions_card, 0, 0)
        grid.addWidget(self.total_words_card, 0, 1)
        grid.addWidget(self.total_time_card, 0, 2)
        grid.addWidget(self.unique_days_card, 0, 3)

        section.layout().addLayout(grid)

    def _build_averages_section(self):
        """Build the averages stats section."""
        section = self._create_section("AVERAGES")

        grid = QGridLayout()
        grid.setSpacing(16)

        self.avg_words_card = StatCard("WORDS/SESSION", "0")
        self.avg_duration_card = StatCard("TIME/SESSION", "0m")
        self.wpm_card = StatCard("WORDS/MINUTE", "0")
        self.sessions_week_card = StatCard("SESSIONS/WEEK", "0")

        grid.addWidget(self.avg_words_card, 0, 0)
        grid.addWidget(self.avg_duration_card, 0, 1)
        grid.addWidget(self.wpm_card, 0, 2)
        grid.addWidget(self.sessions_week_card, 0, 3)

        section.layout().addLayout(grid)

    def _build_streaks_section(self):
        """Build the streaks section."""
        section = self._create_section("STREAKS")

        grid = QGridLayout()
        grid.setSpacing(16)

        self.current_streak_card = StatCard("CURRENT STREAK", "0 days")
        self.longest_streak_card = StatCard("LONGEST STREAK", "0 days")

        grid.addWidget(self.current_streak_card, 0, 0)
        grid.addWidget(self.longest_streak_card, 0, 1)

        section.layout().addLayout(grid)

    def _build_productivity_section(self):
        """Build the productivity insights section."""
        section = self._create_section("PRODUCTIVITY")

        grid = QGridLayout()
        grid.setSpacing(16)

        self.best_day_card = StatCard("BEST DAY", "-", "Most words written")
        self.best_time_card = StatCard("BEST TIME", "-", "Most sessions started")
        self.best_session_card = StatCard("BEST SESSION", "0 words")

        grid.addWidget(self.best_day_card, 0, 0)
        grid.addWidget(self.best_time_card, 0, 1)
        grid.addWidget(self.best_session_card, 0, 2)

        section.layout().addLayout(grid)

    def _build_goal_section(self):
        """Build the goal tracking section."""
        section = self._create_section("DAILY GOAL")

        self.goal_card = GoalProgressCard()
        self.no_goal_label = QLabel("Set a daily word goal in Settings to track your progress.")
        self.no_goal_label.setObjectName("NoGoalLabel")

        section.layout().addWidget(self.goal_card)
        section.layout().addWidget(self.no_goal_label)

    def _create_section(self, title: str) -> QFrame:
        """Create a section with a title."""
        section = QFrame()
        section.setObjectName("StatsSection")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        layout.addWidget(title_label)

        self.content_layout.addWidget(section)
        return section

    def refresh(self):
        """Reload data and update all statistics."""
        sessions = load_all_sessions()
        settings = get_settings()
        daily_goal = settings.writing.daily_word_goal if settings.writing.show_word_goal else 0

        stats = calculate_statistics(sessions, daily_goal)

        self._update_overview(stats)
        self._update_averages(stats)
        self._update_streaks(stats)
        self._update_productivity(stats)
        self._update_goals(stats)

        logger.debug("Statistics refreshed: %d sessions", len(sessions))

    def _update_overview(self, stats: WritingStatistics):
        """Update overview cards."""
        core = stats.core
        self.total_sessions_card.findChild(QLabel, "StatCardValue").setText(
            f"{core.total_sessions:,}"
        )
        self.total_words_card.findChild(QLabel, "StatCardValue").setText(
            f"{core.total_words:,}"
        )
        self.total_time_card.findChild(QLabel, "StatCardValue").setText(
            format_duration(core.total_duration_seconds)
        )
        self.unique_days_card.findChild(QLabel, "StatCardValue").setText(
            f"{core.unique_days:,}"
        )

    def _update_averages(self, stats: WritingStatistics):
        """Update average cards."""
        avg = stats.averages
        self.avg_words_card.findChild(QLabel, "StatCardValue").setText(
            f"{avg.words_per_session:.0f}"
        )
        self.avg_duration_card.findChild(QLabel, "StatCardValue").setText(
            f"{avg.duration_per_session_minutes:.0f}m"
        )
        self.wpm_card.findChild(QLabel, "StatCardValue").setText(
            f"{avg.words_per_minute:.1f}"
        )
        self.sessions_week_card.findChild(QLabel, "StatCardValue").setText(
            f"{avg.sessions_per_week:.1f}"
        )

    def _update_streaks(self, stats: WritingStatistics):
        """Update streak cards."""
        streaks = stats.streaks
        self.current_streak_card.findChild(QLabel, "StatCardValue").setText(
            f"{streaks.current_streak} days"
        )
        self.longest_streak_card.findChild(QLabel, "StatCardValue").setText(
            f"{streaks.longest_streak} days"
        )

    def _update_productivity(self, stats: WritingStatistics):
        """Update productivity cards."""
        prod = stats.productivity

        if prod.most_productive_weekday:
            self.best_day_card.findChild(QLabel, "StatCardValue").setText(
                prod.most_productive_weekday
            )
        else:
            self.best_day_card.findChild(QLabel, "StatCardValue").setText("-")

        if prod.most_productive_hour is not None:
            self.best_time_card.findChild(QLabel, "StatCardValue").setText(
                format_hour(prod.most_productive_hour)
            )
        else:
            self.best_time_card.findChild(QLabel, "StatCardValue").setText("-")

        self.best_session_card.findChild(QLabel, "StatCardValue").setText(
            f"{prod.best_session_words:,} words"
        )

    def _update_goals(self, stats: WritingStatistics):
        """Update goal tracking."""
        goals = stats.goals

        if goals.daily_goal > 0:
            self.goal_card.show()
            self.no_goal_label.hide()
            self.goal_card.update_progress(
                goals.today_words,
                goals.daily_goal,
                goals.goal_streak
            )
        else:
            self.goal_card.hide()
            self.no_goal_label.show()


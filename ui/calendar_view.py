# ui/calendar_view.py

from datetime import date
from typing import Set

from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtGui import QTextCharFormat, QBrush, QColor, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel

from core.storage import load_sessions_for_month
from ui.theme import current_palette


class CalendarView(QWidget):
    """
    A calendar widget that highlights days with completed writing sessions.
    Emits `dateClicked` signal when a date is clicked.
    """
    dateClicked = pyqtSignal(date)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.label = QLabel("Days with writing are highlighted.")
        self.calendar = QCalendarWidget()
        self.calendar.setObjectName("WritingCalendar")
        layout.addWidget(self.calendar)

        layout.addWidget(self.label)
        layout.addWidget(self.calendar)

        # Track which dates are completed for current month
        self.completed_dates: Set[date] = set()

        # When month changes (user clicks arrows), reload highlights
        self.calendar.currentPageChanged.connect(self._on_month_changed)
        self.calendar.clicked.connect(self._on_date_clicked)

        # Initial load
        self.refresh_month()


    def _on_date_clicked(self, qdate: QDate):
        d = date(qdate.year(), qdate.month(), qdate.day())
        self.dateClicked.emit(d)

    def _on_month_changed(self, year: int, month: int) -> None:
        self.refresh_month()

    def refresh_month(self):
        cal = self.calendar
        palette = current_palette()

        # 1. Reset all formatting
        cal.setDateTextFormat(QDate(), QTextCharFormat())

        # Extract current month & year
        qdate = cal.selectedDate()
        year = qdate.year()
        month = qdate.month()

        # ----------------------------------------------------
        # 2. Highlight today's date
        # ----------------------------------------------------
        today = QDate.currentDate()
        fmt_today = QTextCharFormat()
        fmt_today.setBackground(QColor(palette["calendar_today_bg"]))
        fmt_today.setForeground(QColor(palette["calendar_today_fg"]))
        fmt_today.setFontWeight(QFont.Weight.DemiBold)
        cal.setDateTextFormat(today, fmt_today)

        # ----------------------------------------------------
        # 3. Highlight completed sessions (your streak days)
        # ----------------------------------------------------
        from core.streak_days import load_completed_days
        completed_days = load_completed_days()  # list of date objects

        for d in completed_days:
            if d.year == year and d.month == month:
                qd = QDate(d.year, d.month, d.day)

                fmt = QTextCharFormat()
                fmt.setBackground(QColor(palette["calendar_completed_bg"]))
                fmt.setForeground(QColor(palette["calendar_completed_fg"]))
                fmt.setFontWeight(QFont.Weight.Bold)
                fmt.setFontPointSize(11)

                cal.setDateTextFormat(qd, fmt)

    def _clear_highlights(self) -> None:
        """Reset all date formats (for the currently visible month)."""
        # QCalendarWidget doesn't give us all dates, so we can just clear everything.
        # This is OK for small usage.
        default_fmt = QTextCharFormat()
        # Remove formatting of all dates we've previously set:
        for d in self.completed_dates:
            qdate = QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(qdate, default_fmt)


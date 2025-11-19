# ui/calendar_view.py

from datetime import date
from typing import Set

from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtGui import QTextCharFormat, QBrush
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel

from core.storage import load_sessions_for_month


class CalendarView(QWidget):
    dateClicked = pyqtSignal(date)
    
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Days with writing are highlighted.")
        self.calendar = QCalendarWidget()

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
        self.refresh_month(year, month)

    def refresh_month(self, year: int | None = None, month: int | None = None) -> None:
        """
        Reload sessions for the current (or given) month and highlight those days.
        """
        if year is None or month is None:
            qd = self.calendar.selectedDate()
            year = qd.year()
            month = qd.month()

        # Reset formats
        self._clear_highlights()

        # Load sessions for this month
        sessions = load_sessions_for_month(year, month)
        self.completed_dates = {s.session_date for s in sessions}

        # Apply highlights
        fmt = QTextCharFormat()
        fmt.setBackground(QBrush())  # default brush, we’ll set a color via setProperty if needed

        # Slightly different way: use a light background color via Qt style
        # But here we simply set bold:
        fmt.setFontWeight(75)  # QFont.Bold

        for d in self.completed_dates:
            qdate = QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(qdate, fmt)

    def _clear_highlights(self) -> None:
        """Reset all date formats (for the currently visible month)."""
        # QCalendarWidget doesn't give us all dates, so we can just clear everything.
        # This is OK for small usage.
        default_fmt = QTextCharFormat()
        # Remove formatting of all dates we've previously set:
        for d in self.completed_dates:
            qdate = QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(qdate, default_fmt)

# ui/history_view.py

from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPushButton,
)

from core.storage import load_all_sessions
from core.models import WritingSession
from core.search import SessionSearcher, SearchFilters, SearchResult
from core.logging_config import get_logger
from ui.session_detail_dialog import SessionDetailDialog

logger = get_logger("history_view")


class HistoryView(QWidget):
    """
    Past sessions list with search, filter, and sort capabilities.
    - Search bar for full-text search
    - Filters for mode and word count
    - Sort options
    """

    sessionsChanged = pyqtSignal()  # emitted when sessions are deleted

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HistoryViewRoot")

        # Store all sessions and current filtered results
        self._all_sessions: List[WritingSession] = []
        self._current_results: List[SearchResult] = []

        self._build_ui()
        self._apply_style()
        self._connect_signals()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setSpacing(16)

        # Search and filter bar
        search_bar = self._build_search_bar()
        outer.addLayout(search_bar)

        # Results count label
        self.results_label = QLabel("")
        self.results_label.setObjectName("ResultsLabel")
        outer.addWidget(self.results_label)

        # scroll area so the list can grow
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("HistoryScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.inner = QWidget()
        self.inner.setObjectName("HistoryInner")
        self.inner_layout = QVBoxLayout(self.inner)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(0)

        self.scroll_area.setWidget(self.inner)
        outer.addWidget(self.scroll_area)

    def _build_search_bar(self) -> QHBoxLayout:
        """Build the search and filter controls."""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("Search sessions...")
        self.search_input.setClearButtonEnabled(True)
        layout.addWidget(self.search_input, 2)

        # Mode filter
        self.mode_filter = QComboBox()
        self.mode_filter.setObjectName("ModeFilter")
        self.mode_filter.addItem("All Modes", None)
        self.mode_filter.addItem("Free Writing", "free")
        self.mode_filter.addItem("AI Topic", "random_topic")
        layout.addWidget(self.mode_filter)

        # Min words filter
        words_label = QLabel("Min words:")
        words_label.setObjectName("FilterLabel")
        layout.addWidget(words_label)

        self.min_words_spin = QSpinBox()
        self.min_words_spin.setObjectName("WordsFilter")
        self.min_words_spin.setRange(0, 10000)
        self.min_words_spin.setSpecialValueText("Any")
        self.min_words_spin.setSingleStep(50)
        layout.addWidget(self.min_words_spin)

        # Sort options
        sort_label = QLabel("Sort:")
        sort_label.setObjectName("FilterLabel")
        layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.setObjectName("SortCombo")
        self.sort_combo.addItem("Date (Newest)", ("date", True))
        self.sort_combo.addItem("Date (Oldest)", ("date", False))
        self.sort_combo.addItem("Words (Most)", ("words", True))
        self.sort_combo.addItem("Words (Least)", ("words", False))
        self.sort_combo.addItem("Duration (Longest)", ("duration", True))
        self.sort_combo.addItem("Title (A-Z)", ("title", False))
        layout.addWidget(self.sort_combo)

        # Clear filters button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("ClearButton")
        self.clear_button.clicked.connect(self._clear_filters)
        layout.addWidget(self.clear_button)

        return layout

    def _connect_signals(self) -> None:
        """Connect filter controls to refresh."""
        self.search_input.textChanged.connect(self._on_filter_changed)
        self.mode_filter.currentIndexChanged.connect(self._on_filter_changed)
        self.min_words_spin.valueChanged.connect(self._on_filter_changed)
        self.sort_combo.currentIndexChanged.connect(self._on_filter_changed)

    def _clear_filters(self) -> None:
        """Reset all filters to defaults."""
        self.search_input.clear()
        self.mode_filter.setCurrentIndex(0)
        self.min_words_spin.setValue(0)
        self.sort_combo.setCurrentIndex(0)

    def _on_filter_changed(self) -> None:
        """Called when any filter changes."""
        self._apply_filters()

    def _clear_items(self) -> None:
        layout = self.inner_layout

        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue  # silent pylance warning

            w = item.widget()
            if w is not None:
                w.deleteLater()

    # ------------------------------------------------------------------ Public API

    def refresh(self) -> None:
        """Reload all sessions and apply current filters."""
        self._all_sessions = load_all_sessions()
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Apply current filters and rebuild the list."""
        if not self._all_sessions:
            self._clear_items()
            self._show_empty_state("No sessions yet. Start a new one to see it here.")
            self.results_label.setText("")
            return

        # Build filters from UI state
        filters = SearchFilters(
            query=self.search_input.text().strip(),
            mode=self.mode_filter.currentData(),
            min_words=self.min_words_spin.value() if self.min_words_spin.value() > 0 else None,
        )

        # Get sort options
        sort_data = self.sort_combo.currentData()
        sort_by, sort_descending = sort_data if sort_data else ("date", True)

        # Search
        searcher = SessionSearcher(self._all_sessions)
        self._current_results = searcher.search(filters, sort_by, sort_descending)

        # Update results count
        total = len(self._all_sessions)
        shown = len(self._current_results)
        if filters.query or filters.mode or filters.min_words:
            self.results_label.setText(f"Showing {shown} of {total} sessions")
        else:
            self.results_label.setText(f"{total} sessions")

        # Rebuild list
        self._clear_items()

        if not self._current_results:
            self._show_empty_state("No sessions match your search criteria.")
            return

        for idx, result in enumerate(self._current_results):
            card = self._make_card(result.session, result.snippet if filters.query else None)
            self.inner_layout.addWidget(card)

            # separator line between rows
            if idx < len(self._current_results) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Plain)
                line.setObjectName("HistoryDivider")
                self.inner_layout.addWidget(line)

        self.inner_layout.addStretch()

    def _show_empty_state(self, message: str) -> None:
        """Show an empty state message."""
        empty = QLabel(message)
        empty.setObjectName("EmptyHistoryLabel")
        empty.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.inner_layout.addWidget(empty)
        self.inner_layout.addStretch()

    # ------------------------------------------------------------------ Card creation

    def _make_card(self, sess: WritingSession, snippet: Optional[str] = None) -> QWidget:
        card = QWidget()
        card.setObjectName("SessionCard")

        row = QHBoxLayout(card)
        row.setContentsMargins(0, 16, 0, 16)
        row.setSpacing(16)

        # left: title + date + optional snippet
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(4)

        title = sess.title or sess.session_date.isoformat()
        title_label = QLabel(title)
        title_label.setObjectName("SessionTitle")

        # Date and word count
        date_str = sess.session_date.strftime("%m/%d/%Y")
        info_label = QLabel(f"{date_str}  •  {sess.word_count} words")
        info_label.setObjectName("SessionDate")

        text_col.addWidget(title_label)
        text_col.addWidget(info_label)

        # Show snippet if searching
        if snippet:
            snippet_label = QLabel(snippet)
            snippet_label.setObjectName("SessionSnippet")
            snippet_label.setWordWrap(True)
            snippet_label.setMaximumWidth(500)
            text_col.addWidget(snippet_label)

        # right: mode badge
        mode_label = QLabel(self._mode_label(sess.mode))
        mode_label.setObjectName("SessionModeBadge")
        mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row.addLayout(text_col, 1)
        row.addStretch()
        row.addWidget(mode_label, 0, Qt.AlignmentFlag.AlignVCenter)

        # simple click-to-open behavior
        def _open_detail(event):
            if event.button() == Qt.MouseButton.LeftButton:
                dlg = SessionDetailDialog(sess, self)
                dlg.exec()

        card.mousePressEvent = _open_detail  # type: ignore[assignment]

        return card

    @staticmethod
    def _mode_label(mode: str | None) -> str:
        if mode == "free":
            return "FREE"
        if mode == "random_topic":
            return "AI PROMPT"
        return (mode or "").upper()

    # ------------------------------------------------------------------ Styling

    def _apply_style(self) -> None:
        self.setStyleSheet("""
        QWidget#HistoryViewRoot {
            background-color: #000000;
        }
        QWidget#HistoryInner {
            background-color: #000000;
        }
        QScrollArea#HistoryScrollArea {
            background: transparent;
            border: none;
        }

        QLabel#EmptyHistoryLabel {
            font-size: 14px;
            color: #888888;
        }

        QLabel#ResultsLabel {
            font-size: 13px;
            color: #888888;
        }

        /* Search and filter controls */
        QLineEdit#SearchInput {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
        }
        QLineEdit#SearchInput:focus {
            border-color: #00b894;
        }

        QComboBox#ModeFilter, QComboBox#SortCombo {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 120px;
        }
        QComboBox#ModeFilter::drop-down, QComboBox#SortCombo::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #1a1a1a;
            color: #ffffff;
            selection-background-color: #333333;
        }

        QSpinBox#WordsFilter {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 6px;
            min-width: 80px;
        }

        QLabel#FilterLabel {
            color: #888888;
            font-size: 13px;
        }

        QPushButton#ClearButton {
            background-color: #333333;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
        }
        QPushButton#ClearButton:hover {
            background-color: #444444;
        }

        QWidget#SessionCard {
            background-color: #000000;
        }

        QLabel#SessionTitle {
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
        }

        QLabel#SessionDate {
            font-size: 13px;
            color: #888888;
        }

        QLabel#SessionSnippet {
            font-size: 13px;
            color: #aaaaaa;
            font-style: italic;
        }

        QLabel#SessionModeBadge {
            background-color: #333333;
            color: #ffffff;
            font-size: 11px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 3px;
        }

        QFrame#HistoryDivider {
            background-color: #333333;
            max-height: 1px;
            min-height: 1px;
        }
        """)

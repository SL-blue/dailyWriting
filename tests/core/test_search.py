"""
Tests for core/search.py - search and filter functionality.
"""

import pytest
from datetime import date, datetime

from core.search import (
    SessionSearcher,
    SearchFilters,
    SearchResult,
    search_sessions,
    highlight_matches,
)
from core.models import WritingSession


def make_session(
    id: str = "test",
    title: str = "Test Session",
    content: str = "Test content",
    session_date: date = None,
    mode: str = "free",
    topic: str = None,
    word_count: int = 10,
    duration_seconds: int = 600,
) -> WritingSession:
    """Helper to create test sessions."""
    if session_date is None:
        session_date = date(2025, 1, 15)

    return WritingSession(
        id=id,
        title=title,
        session_date=session_date,
        mode=mode,
        topic=topic,
        content=content,
        start_time=datetime(2025, 1, 15, 10, 0, 0),
        end_time=datetime(2025, 1, 15, 10, 10, 0),
        duration_seconds=duration_seconds,
        char_count=len(content),
        word_count=word_count,
    )


class TestSearchFilters:
    """Tests for SearchFilters dataclass."""

    def test_default_values(self):
        filters = SearchFilters()
        assert filters.query == ""
        assert filters.date_from is None
        assert filters.mode is None
        assert filters.min_words is None


class TestSessionSearcher:
    """Tests for SessionSearcher class."""

    @pytest.fixture
    def sample_sessions(self):
        return [
            make_session(
                id="1",
                title="Morning Writing",
                content="Today I wrote about the sunrise.",
                session_date=date(2025, 1, 15),
                mode="free",
                word_count=50,
            ),
            make_session(
                id="2",
                title="Mystery Story",
                content="The detective found a clue in the library.",
                session_date=date(2025, 1, 16),
                mode="random_topic",
                topic="Write a mystery story",
                word_count=100,
            ),
            make_session(
                id="3",
                title="Evening Thoughts",
                content="Reflecting on the day's events.",
                session_date=date(2025, 1, 17),
                mode="free",
                word_count=30,
            ),
        ]

    def test_search_no_filters(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters())

        assert len(results) == 3

    def test_search_by_query_in_title(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(query="Morning"))

        assert len(results) == 1
        assert results[0].session.title == "Morning Writing"
        assert "title" in results[0].matched_fields

    def test_search_by_query_in_content(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(query="detective"))

        assert len(results) == 1
        assert results[0].session.title == "Mystery Story"
        assert "content" in results[0].matched_fields

    def test_search_by_query_in_topic(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(query="mystery"))

        assert len(results) == 1
        assert "topic" in results[0].matched_fields

    def test_search_case_insensitive(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(query="MORNING"))

        assert len(results) == 1

    def test_filter_by_mode(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(mode="free"))

        assert len(results) == 2
        assert all(r.session.mode == "free" for r in results)

    def test_filter_by_date_range(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(
            date_from=date(2025, 1, 16),
            date_to=date(2025, 1, 16)
        ))

        assert len(results) == 1
        assert results[0].session.session_date == date(2025, 1, 16)

    def test_filter_by_min_words(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(min_words=50))

        assert len(results) == 2
        assert all(r.session.word_count >= 50 for r in results)

    def test_filter_by_max_words(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(max_words=50))

        assert len(results) == 2
        assert all(r.session.word_count <= 50 for r in results)

    def test_combined_filters(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(
            mode="free",
            min_words=40,
        ))

        assert len(results) == 1
        assert results[0].session.title == "Morning Writing"

    def test_sort_by_date_descending(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(
            SearchFilters(),
            sort_by="date",
            sort_descending=True
        )

        dates = [r.session.session_date for r in results]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_words_descending(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(
            SearchFilters(),
            sort_by="words",
            sort_descending=True
        )

        words = [r.session.word_count for r in results]
        assert words == sorted(words, reverse=True)

    def test_sort_by_title_ascending(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(
            SearchFilters(),
            sort_by="title",
            sort_descending=False
        )

        titles = [r.session.title.lower() for r in results]
        assert titles == sorted(titles)

    def test_snippet_creation(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(query="detective"))

        assert len(results) == 1
        assert "detective" in results[0].snippet

    def test_no_results(self, sample_sessions):
        searcher = SessionSearcher(sample_sessions)
        results = searcher.search(SearchFilters(query="xyz123notfound"))

        assert len(results) == 0


class TestSearchSessionsFunction:
    """Tests for the convenience search_sessions function."""

    def test_basic_search(self):
        sessions = [
            make_session(id="1", title="Test One"),
            make_session(id="2", title="Test Two"),
        ]

        results = search_sessions(sessions, query="One")

        assert len(results) == 1
        assert results[0].session.title == "Test One"


class TestHighlightMatches:
    """Tests for highlight_matches function."""

    def test_basic_highlight(self):
        result = highlight_matches("Hello world", "world")
        assert result == "Hello **world**"

    def test_case_insensitive_highlight(self):
        result = highlight_matches("Hello World", "world")
        assert result == "Hello **World**"

    def test_multiple_matches(self):
        result = highlight_matches("test one test two test", "test")
        assert result.count("**test**") == 3

    def test_custom_markers(self):
        result = highlight_matches("Hello world", "world", "<b>", "</b>")
        assert result == "Hello <b>world</b>"

    def test_no_match(self):
        result = highlight_matches("Hello world", "xyz")
        assert result == "Hello world"

    def test_empty_query(self):
        result = highlight_matches("Hello world", "")
        assert result == "Hello world"

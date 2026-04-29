"""
Search and filter functionality for writing sessions.

Features:
- Full-text search across title, content, topic
- Filter by date range, mode, word count, duration
- Sort by various fields
"""

import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Callable

from .models import WritingSession
from .logging_config import get_logger

logger = get_logger("search")


@dataclass
class SearchFilters:
    """Filters to apply when searching sessions."""

    # Text search (searches title, content, topic)
    query: str = ""

    # Date range filter
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    # Mode filter
    mode: Optional[str] = None  # "free", "random_topic", or None for all

    # Word count range
    min_words: Optional[int] = None
    max_words: Optional[int] = None

    # Duration range (in seconds)
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None


@dataclass
class SearchResult:
    """A search result with the session and match information."""
    session: WritingSession
    # Which fields matched the search query
    matched_fields: List[str]
    # Snippet of content with match highlighted (for display)
    snippet: str = ""


class SessionSearcher:
    """Search and filter sessions."""

    def __init__(self, sessions: List[WritingSession]):
        """
        Initialize with a list of sessions to search.

        Args:
            sessions: List of WritingSession objects to search.
        """
        self.sessions = sessions

    def search(
        self,
        filters: SearchFilters,
        sort_by: str = "date",
        sort_descending: bool = True
    ) -> List[SearchResult]:
        """
        Search sessions with filters and sorting.

        Args:
            filters: SearchFilters object with search criteria.
            sort_by: Field to sort by ("date", "words", "duration", "title").
            sort_descending: If True, sort in descending order.

        Returns:
            List of SearchResult objects matching the criteria.
        """
        results = []

        for session in self.sessions:
            # Apply filters
            if not self._matches_filters(session, filters):
                continue

            # Check text search
            matched_fields = []
            if filters.query:
                matched_fields = self._get_matched_fields(session, filters.query)
                if not matched_fields:
                    continue

            # Create result with snippet
            snippet = self._create_snippet(session, filters.query)
            results.append(SearchResult(
                session=session,
                matched_fields=matched_fields,
                snippet=snippet
            ))

        # Sort results
        results = self._sort_results(results, sort_by, sort_descending)

        logger.debug("Search found %d results for query '%s'", len(results), filters.query)
        return results

    def _matches_filters(self, session: WritingSession, filters: SearchFilters) -> bool:
        """Check if session matches all non-text filters."""

        # Date range
        if filters.date_from and session.session_date < filters.date_from:
            return False
        if filters.date_to and session.session_date > filters.date_to:
            return False

        # Mode
        if filters.mode and session.mode != filters.mode:
            return False

        # Word count range
        if filters.min_words is not None and session.word_count < filters.min_words:
            return False
        if filters.max_words is not None and session.word_count > filters.max_words:
            return False

        # Duration range
        if filters.min_duration is not None and session.duration_seconds < filters.min_duration:
            return False
        if filters.max_duration is not None and session.duration_seconds > filters.max_duration:
            return False

        return True

    def _get_matched_fields(self, session: WritingSession, query: str) -> List[str]:
        """Get list of fields that match the query."""
        query_lower = query.lower()
        matched = []

        if query_lower in session.title.lower():
            matched.append("title")

        if query_lower in session.content.lower():
            matched.append("content")

        if session.topic and query_lower in session.topic.lower():
            matched.append("topic")

        return matched

    def _create_snippet(self, session: WritingSession, query: str, max_length: int = 150) -> str:
        """Create a content snippet with the search term highlighted."""
        if not query:
            # No search query, return beginning of content
            content = session.content.strip()
            if len(content) <= max_length:
                return content
            return content[:max_length].rsplit(" ", 1)[0] + "..."

        content = session.content
        query_lower = query.lower()
        content_lower = content.lower()

        # Find the first occurrence of the query
        pos = content_lower.find(query_lower)
        if pos == -1:
            # Query not in content, check topic
            if session.topic and query_lower in session.topic.lower():
                return f"[Topic: {session.topic[:100]}...]"
            return content[:max_length] + "..." if len(content) > max_length else content

        # Extract context around the match
        start = max(0, pos - 50)
        end = min(len(content), pos + len(query) + 100)

        snippet = content[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def _sort_results(
        self,
        results: List[SearchResult],
        sort_by: str,
        descending: bool
    ) -> List[SearchResult]:
        """Sort results by the specified field."""

        sort_keys: dict[str, Callable[[SearchResult], any]] = {
            "date": lambda r: r.session.session_date,
            "words": lambda r: r.session.word_count,
            "duration": lambda r: r.session.duration_seconds,
            "title": lambda r: r.session.title.lower(),
        }

        key_func = sort_keys.get(sort_by, sort_keys["date"])
        return sorted(results, key=key_func, reverse=descending)


def search_sessions(
    sessions: List[WritingSession],
    query: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    mode: Optional[str] = None,
    min_words: Optional[int] = None,
    max_words: Optional[int] = None,
    sort_by: str = "date",
    sort_descending: bool = True
) -> List[SearchResult]:
    """
    Convenience function to search sessions.

    Args:
        sessions: List of sessions to search.
        query: Text to search for.
        date_from: Start of date range.
        date_to: End of date range.
        mode: Filter by mode ("free" or "random_topic").
        min_words: Minimum word count.
        max_words: Maximum word count.
        sort_by: Field to sort by.
        sort_descending: Sort direction.

    Returns:
        List of SearchResult objects.
    """
    filters = SearchFilters(
        query=query,
        date_from=date_from,
        date_to=date_to,
        mode=mode,
        min_words=min_words,
        max_words=max_words,
    )

    searcher = SessionSearcher(sessions)
    return searcher.search(filters, sort_by, sort_descending)


def highlight_matches(text: str, query: str, before: str = "**", after: str = "**") -> str:
    """
    Highlight search query matches in text.

    Args:
        text: The text to highlight in.
        query: The search query to highlight.
        before: String to insert before matches.
        after: String to insert after matches.

    Returns:
        Text with matches highlighted.
    """
    if not query:
        return text

    # Case-insensitive replacement while preserving original case
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"{before}{m.group()}{after}", text)

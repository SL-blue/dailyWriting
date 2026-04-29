"""
Shared pytest fixtures for DailyWriting tests.
"""

import pytest
from datetime import date, datetime
from pathlib import Path
import tempfile
import shutil

from core.models import WritingSession


@pytest.fixture
def sample_session() -> WritingSession:
    """Create a sample WritingSession for testing."""
    return WritingSession(
        id="test-session-123",
        title="Test Session",
        session_date=date(2025, 1, 15),
        mode="free",
        topic=None,
        content="This is test content for the session.",
        start_time=datetime(2025, 1, 15, 10, 0, 0),
        end_time=datetime(2025, 1, 15, 10, 30, 0),
        duration_seconds=1800,
        char_count=40,
        word_count=8,
    )


@pytest.fixture
def sample_ai_session() -> WritingSession:
    """Create a sample AI-generated topic session for testing."""
    return WritingSession(
        id="test-ai-session-456",
        title="AI Writing Session",
        session_date=date(2025, 1, 16),
        mode="random_topic",
        topic="Write about a mysterious letter found in an old book.",
        content="The letter was yellowed with age...",
        start_time=datetime(2025, 1, 16, 14, 0, 0),
        end_time=datetime(2025, 1, 16, 14, 45, 0),
        duration_seconds=2700,
        char_count=35,
        word_count=7,
    )


@pytest.fixture
def temp_sessions_dir(tmp_path: Path, monkeypatch):
    """Create a temporary sessions directory and patch storage to use it."""
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()

    # Patch the SESSIONS_DIR in storage module
    import core.storage as storage
    monkeypatch.setattr(storage, "SESSIONS_DIR", sessions_dir)

    return sessions_dir


@pytest.fixture
def multiple_sessions() -> list[WritingSession]:
    """Create multiple sessions for streak testing."""
    return [
        WritingSession(
            id=f"session-{i}",
            title=f"Session {i}",
            session_date=date(2025, 1, 10 + i),
            mode="free",
            topic=None,
            content=f"Content for session {i}",
            start_time=datetime(2025, 1, 10 + i, 10, 0, 0),
            end_time=datetime(2025, 1, 10 + i, 10, 30, 0),
            duration_seconds=1800,
            char_count=20,
            word_count=4,
        )
        for i in range(5)  # Sessions on Jan 10, 11, 12, 13, 14
    ]

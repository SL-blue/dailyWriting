"""
Tests for core/storage.py - session persistence.
"""

import pytest
import json
from datetime import date, datetime

from core.storage import (
    session_to_dict,
    dict_to_session,
    save_session,
    load_sessions_for_date,
    load_all_sessions,
    delete_session,
    get_session_path,
)
from core.models import WritingSession


class TestSessionSerialization:
    """Tests for session <-> dict conversion."""

    def test_session_to_dict(self, sample_session):
        result = session_to_dict(sample_session)

        assert result["id"] == "test-session-123"
        assert result["title"] == "Test Session"
        assert result["session_date"] == "2025-01-15"
        assert result["mode"] == "free"
        assert result["topic"] is None
        assert result["content"] == "This is test content for the session."
        assert result["start_time"] == "2025-01-15T10:00:00"
        assert result["end_time"] == "2025-01-15T10:30:00"
        assert result["duration_seconds"] == 1800
        assert result["char_count"] == 40
        assert result["word_count"] == 8

    def test_session_to_dict_with_topic(self, sample_ai_session):
        result = session_to_dict(sample_ai_session)

        assert result["mode"] == "random_topic"
        assert result["topic"] == "Write about a mysterious letter found in an old book."

    def test_session_to_dict_no_end_time(self, sample_session):
        sample_session.end_time = None
        result = session_to_dict(sample_session)

        assert result["end_time"] is None

    def test_dict_to_session(self):
        data = {
            "id": "abc123",
            "title": "My Session",
            "session_date": "2025-02-20",
            "mode": "free",
            "topic": None,
            "content": "Test content here",
            "start_time": "2025-02-20T09:00:00",
            "end_time": "2025-02-20T09:30:00",
            "duration_seconds": 1800,
            "char_count": 17,
            "word_count": 3,
        }

        session = dict_to_session(data)

        assert session.id == "abc123"
        assert session.title == "My Session"
        assert session.session_date == date(2025, 2, 20)
        assert session.mode == "free"
        assert session.topic is None
        assert session.content == "Test content here"
        assert session.start_time == datetime(2025, 2, 20, 9, 0, 0)
        assert session.end_time == datetime(2025, 2, 20, 9, 30, 0)
        assert session.duration_seconds == 1800
        assert session.char_count == 17
        assert session.word_count == 3

    def test_dict_to_session_missing_title_uses_date(self):
        """Old sessions without title field should default to date."""
        data = {
            "id": "old-session",
            "session_date": "2024-12-25",
            "mode": "free",
            "topic": None,
            "content": "Old content",
            "start_time": "2024-12-25T10:00:00",
            "end_time": None,
            "duration_seconds": 600,
            "char_count": 11,
            "word_count": 2,
        }

        session = dict_to_session(data)

        assert session.title == "2024-12-25"

    def test_roundtrip_serialization(self, sample_session):
        """Converting to dict and back should preserve all data."""
        data = session_to_dict(sample_session)
        restored = dict_to_session(data)

        assert restored.id == sample_session.id
        assert restored.title == sample_session.title
        assert restored.session_date == sample_session.session_date
        assert restored.mode == sample_session.mode
        assert restored.topic == sample_session.topic
        assert restored.content == sample_session.content
        assert restored.start_time == sample_session.start_time
        assert restored.end_time == sample_session.end_time
        assert restored.duration_seconds == sample_session.duration_seconds
        assert restored.char_count == sample_session.char_count
        assert restored.word_count == sample_session.word_count


class TestSessionPersistence:
    """Tests for file save/load operations."""

    def test_save_and_load_session(self, sample_session, temp_sessions_dir):
        save_session(sample_session)

        # Check file was created
        files = list(temp_sessions_dir.glob("*.json"))
        assert len(files) == 1

        # Load and verify
        loaded = load_sessions_for_date(sample_session.session_date)
        assert len(loaded) == 1
        assert loaded[0].id == sample_session.id

    def test_load_sessions_for_date_empty(self, temp_sessions_dir):
        sessions = load_sessions_for_date(date(2025, 1, 1))
        assert sessions == []

    def test_load_all_sessions(self, sample_session, sample_ai_session, temp_sessions_dir):
        save_session(sample_session)
        save_session(sample_ai_session)

        all_sessions = load_all_sessions()

        assert len(all_sessions) == 2
        ids = {s.id for s in all_sessions}
        assert sample_session.id in ids
        assert sample_ai_session.id in ids

    def test_delete_session(self, sample_session, temp_sessions_dir):
        save_session(sample_session)

        # Verify exists
        files = list(temp_sessions_dir.glob("*.json"))
        assert len(files) == 1

        # Delete
        delete_session(sample_session)

        # Verify deleted
        files = list(temp_sessions_dir.glob("*.json"))
        assert len(files) == 0

    def test_delete_nonexistent_session(self, sample_session, temp_sessions_dir):
        # Should not raise even if file doesn't exist
        delete_session(sample_session)

    def test_get_session_path(self, sample_session, temp_sessions_dir):
        path = get_session_path(sample_session)

        assert path.name == "2025-01-15-test-session-123.json"
        assert path.parent == temp_sessions_dir

    def test_load_all_sessions_ignores_invalid_json(self, temp_sessions_dir):
        # Create a valid session
        valid_session = WritingSession(
            id="valid",
            title="Valid",
            session_date=date(2025, 1, 1),
            mode="free",
            topic=None,
            content="test",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=None,
            duration_seconds=0,
            char_count=4,
            word_count=1,
        )
        save_session(valid_session)

        # Create an invalid JSON file
        invalid_file = temp_sessions_dir / "2025-01-02-invalid.json"
        invalid_file.write_text("{ invalid json }")

        # Should load valid session and skip invalid
        sessions = load_all_sessions()
        assert len(sessions) == 1
        assert sessions[0].id == "valid"

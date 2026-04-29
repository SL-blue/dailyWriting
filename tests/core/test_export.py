"""
Tests for core/export.py - session export functionality.
"""

import pytest
import json
from pathlib import Path

from core.export import (
    export_to_markdown,
    export_to_text,
    export_to_json,
    export_to_html,
    export_session,
    export_sessions_bulk,
    get_export_extension,
)


class TestExportToMarkdown:
    """Tests for Markdown export."""

    def test_basic_export(self, sample_session):
        result = export_to_markdown(sample_session)

        assert "# Test Session" in result
        assert "This is test content for the session." in result

    def test_with_metadata(self, sample_session):
        result = export_to_markdown(sample_session, include_metadata=True)

        assert "**Date:** 2025-01-15" in result
        assert "**Mode:** Free Writing" in result
        assert "**Words:** 8" in result

    def test_without_metadata(self, sample_session):
        result = export_to_markdown(sample_session, include_metadata=False)

        assert "**Date:**" not in result
        assert "**Mode:**" not in result
        assert "# Test Session" in result

    def test_with_topic(self, sample_ai_session):
        result = export_to_markdown(sample_ai_session)

        assert "## Prompt" in result
        assert "mysterious letter" in result
        assert "AI Topic" in result


class TestExportToText:
    """Tests for plain text export."""

    def test_basic_export(self, sample_session):
        result = export_to_text(sample_session)

        assert "TEST SESSION" in result
        assert "This is test content for the session." in result

    def test_with_metadata(self, sample_session):
        result = export_to_text(sample_session, include_metadata=True)

        assert "Date: 2025-01-15" in result
        assert "Words: 8" in result

    def test_with_topic(self, sample_ai_session):
        result = export_to_text(sample_ai_session)

        assert "PROMPT:" in result
        assert "mysterious letter" in result


class TestExportToJson:
    """Tests for JSON export."""

    def test_basic_export(self, sample_session):
        result = export_to_json(sample_session)
        data = json.loads(result)

        assert data["title"] == "Test Session"
        assert data["content"] == "This is test content for the session."
        assert data["word_count"] == 8

    def test_with_metadata(self, sample_session):
        result = export_to_json(sample_session, include_metadata=True)
        data = json.loads(result)

        assert "id" in data
        assert "session_date" in data
        assert "duration_seconds" in data

    def test_without_metadata(self, sample_session):
        result = export_to_json(sample_session, include_metadata=False)
        data = json.loads(result)

        assert "title" in data
        assert "content" in data
        assert "id" not in data
        assert "duration_seconds" not in data


class TestExportToHtml:
    """Tests for HTML export."""

    def test_basic_export(self, sample_session):
        result = export_to_html(sample_session)

        assert "<!DOCTYPE html>" in result
        assert "<title>Test Session</title>" in result
        assert "This is test content for the session." in result

    def test_escapes_html(self, sample_session):
        sample_session.content = "<script>alert('xss')</script>"
        result = export_to_html(sample_session)

        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_with_topic(self, sample_ai_session):
        result = export_to_html(sample_ai_session)

        assert "class='prompt'" in result
        assert "mysterious letter" in result


class TestExportSession:
    """Tests for file export."""

    def test_export_markdown_file(self, sample_session, tmp_path):
        output_path = tmp_path / "test.md"
        export_session(sample_session, output_path, format="markdown")

        assert output_path.exists()
        content = output_path.read_text()
        assert "# Test Session" in content

    def test_export_json_file(self, sample_session, tmp_path):
        output_path = tmp_path / "test.json"
        export_session(sample_session, output_path, format="json")

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data["title"] == "Test Session"

    def test_creates_parent_directories(self, sample_session, tmp_path):
        output_path = tmp_path / "nested" / "dir" / "test.md"
        export_session(sample_session, output_path, format="markdown")

        assert output_path.exists()

    def test_invalid_format_raises(self, sample_session, tmp_path):
        output_path = tmp_path / "test.xyz"
        with pytest.raises(ValueError, match="Unsupported export format"):
            export_session(sample_session, output_path, format="xyz")


class TestExportSessionsBulk:
    """Tests for bulk export."""

    def test_bulk_export(self, sample_session, sample_ai_session, tmp_path):
        sessions = [sample_session, sample_ai_session]
        exported = export_sessions_bulk(sessions, tmp_path, format="markdown")

        assert len(exported) == 2
        assert all(p.exists() for p in exported)

    def test_creates_output_directory(self, sample_session, tmp_path):
        output_dir = tmp_path / "new_dir"
        export_sessions_bulk([sample_session], output_dir, format="txt")

        assert output_dir.exists()
        assert len(list(output_dir.glob("*.txt"))) == 1


class TestGetExportExtension:
    """Tests for extension helper."""

    def test_known_formats(self):
        assert get_export_extension("markdown") == ".md"
        assert get_export_extension("txt") == ".txt"
        assert get_export_extension("json") == ".json"
        assert get_export_extension("html") == ".html"

    def test_unknown_format(self):
        assert get_export_extension("unknown") == ".txt"

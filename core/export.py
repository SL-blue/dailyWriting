"""
Export functionality for writing sessions.

Supports exporting to:
- Markdown (.md)
- Plain Text (.txt)
- JSON (.json)
- HTML (.html)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import WritingSession
from .storage import session_to_dict
from .logging_config import get_logger

logger = get_logger("export")


def export_to_markdown(
    session: WritingSession,
    include_metadata: bool = True
) -> str:
    """
    Export a session to Markdown format.

    Args:
        session: The WritingSession to export.
        include_metadata: Whether to include metadata header.

    Returns:
        Markdown formatted string.
    """
    lines = []

    # Title
    lines.append(f"# {session.title}")
    lines.append("")

    if include_metadata:
        lines.append(f"**Date:** {session.session_date.isoformat()}")
        lines.append(f"**Mode:** {'AI Topic' if session.mode == 'random_topic' else 'Free Writing'}")

        if session.duration_seconds:
            minutes = session.duration_seconds // 60
            seconds = session.duration_seconds % 60
            lines.append(f"**Duration:** {minutes}m {seconds}s")

        lines.append(f"**Words:** {session.word_count}")
        lines.append(f"**Characters:** {session.char_count}")
        lines.append("")

    # Topic/prompt if present
    if session.topic:
        lines.append("## Prompt")
        lines.append("")
        lines.append(f"> {session.topic}")
        lines.append("")

    # Content
    lines.append("## Content")
    lines.append("")
    lines.append(session.content)

    return "\n".join(lines)


def export_to_text(
    session: WritingSession,
    include_metadata: bool = True
) -> str:
    """
    Export a session to plain text format.

    Args:
        session: The WritingSession to export.
        include_metadata: Whether to include metadata header.

    Returns:
        Plain text formatted string.
    """
    lines = []

    lines.append(session.title.upper())
    lines.append("=" * len(session.title))
    lines.append("")

    if include_metadata:
        lines.append(f"Date: {session.session_date.isoformat()}")
        lines.append(f"Mode: {'AI Topic' if session.mode == 'random_topic' else 'Free Writing'}")

        if session.duration_seconds:
            minutes = session.duration_seconds // 60
            lines.append(f"Duration: {minutes} minutes")

        lines.append(f"Words: {session.word_count}")
        lines.append("")
        lines.append("-" * 40)
        lines.append("")

    if session.topic:
        lines.append("PROMPT:")
        lines.append(session.topic)
        lines.append("")
        lines.append("-" * 40)
        lines.append("")

    lines.append(session.content)

    return "\n".join(lines)


def export_to_json(
    session: WritingSession,
    include_metadata: bool = True
) -> str:
    """
    Export a session to JSON format.

    Args:
        session: The WritingSession to export.
        include_metadata: Whether to include all metadata (if False, only content).

    Returns:
        JSON formatted string.
    """
    if include_metadata:
        data = session_to_dict(session)
    else:
        data = {
            "title": session.title,
            "content": session.content,
        }
        if session.topic:
            data["topic"] = session.topic

    return json.dumps(data, indent=2, ensure_ascii=False)


def export_to_html(
    session: WritingSession,
    include_metadata: bool = True
) -> str:
    """
    Export a session to HTML format with styling.

    Args:
        session: The WritingSession to export.
        include_metadata: Whether to include metadata section.

    Returns:
        HTML formatted string.
    """
    # Escape HTML entities in content
    def escape_html(text: str) -> str:
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("\n", "<br>\n"))

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        f"  <title>{escape_html(session.title)}</title>",
        "  <style>",
        "    body {",
        "      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
        "      max-width: 800px;",
        "      margin: 40px auto;",
        "      padding: 20px;",
        "      line-height: 1.6;",
        "      color: #333;",
        "    }",
        "    h1 { color: #1a1a1a; border-bottom: 2px solid #00b894; padding-bottom: 10px; }",
        "    .metadata { color: #666; font-size: 14px; margin-bottom: 20px; }",
        "    .metadata span { margin-right: 20px; }",
        "    .prompt { background: #f5f5f5; padding: 15px; border-left: 4px solid #ff3b30; margin: 20px 0; }",
        "    .prompt-label { font-weight: bold; color: #ff3b30; margin-bottom: 5px; }",
        "    .content { white-space: pre-wrap; font-size: 16px; }",
        "    @media print { body { margin: 20px; } }",
        "  </style>",
        "</head>",
        "<body>",
        f"  <h1>{escape_html(session.title)}</h1>",
    ]

    if include_metadata:
        mode_text = "AI Topic" if session.mode == "random_topic" else "Free Writing"
        duration_text = ""
        if session.duration_seconds:
            minutes = session.duration_seconds // 60
            duration_text = f"<span>Duration: {minutes} min</span>"

        html_parts.append("  <div class='metadata'>")
        html_parts.append(f"    <span>Date: {session.session_date.isoformat()}</span>")
        html_parts.append(f"    <span>Mode: {mode_text}</span>")
        if duration_text:
            html_parts.append(f"    {duration_text}")
        html_parts.append(f"    <span>Words: {session.word_count}</span>")
        html_parts.append("  </div>")

    if session.topic:
        html_parts.append("  <div class='prompt'>")
        html_parts.append("    <div class='prompt-label'>Prompt</div>")
        html_parts.append(f"    <div>{escape_html(session.topic)}</div>")
        html_parts.append("  </div>")

    html_parts.append("  <div class='content'>")
    html_parts.append(f"    {escape_html(session.content)}")
    html_parts.append("  </div>")
    html_parts.append("</body>")
    html_parts.append("</html>")

    return "\n".join(html_parts)


def export_session(
    session: WritingSession,
    output_path: Path,
    format: str = "markdown",
    include_metadata: bool = True
) -> None:
    """
    Export a single session to a file.

    Args:
        session: The WritingSession to export.
        output_path: Path to the output file.
        format: Export format ("markdown", "txt", "json", "html").
        include_metadata: Whether to include metadata.

    Raises:
        ValueError: If format is not supported.
        OSError: If file cannot be written.
    """
    exporters = {
        "markdown": export_to_markdown,
        "txt": export_to_text,
        "json": export_to_json,
        "html": export_to_html,
    }

    if format not in exporters:
        raise ValueError(f"Unsupported export format: {format}")

    content = exporters[format](session, include_metadata)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    logger.info("Exported session %s to %s", session.id, output_path)


def export_sessions_bulk(
    sessions: List[WritingSession],
    output_dir: Path,
    format: str = "markdown",
    include_metadata: bool = True
) -> List[Path]:
    """
    Export multiple sessions to a directory.

    Args:
        sessions: List of WritingSession objects to export.
        output_dir: Directory to save exported files.
        format: Export format ("markdown", "txt", "json", "html").
        include_metadata: Whether to include metadata.

    Returns:
        List of paths to exported files.
    """
    extensions = {
        "markdown": ".md",
        "txt": ".txt",
        "json": ".json",
        "html": ".html",
    }

    if format not in extensions:
        raise ValueError(f"Unsupported export format: {format}")

    output_dir.mkdir(parents=True, exist_ok=True)
    exported_paths = []

    for session in sessions:
        # Create filename from date and title
        safe_title = "".join(c for c in session.title if c.isalnum() or c in " -_").strip()
        safe_title = safe_title[:50]  # Limit length
        filename = f"{session.session_date.isoformat()}_{safe_title}{extensions[format]}"
        output_path = output_dir / filename

        export_session(session, output_path, format, include_metadata)
        exported_paths.append(output_path)

    logger.info("Exported %d sessions to %s", len(sessions), output_dir)
    return exported_paths


def get_export_extension(format: str) -> str:
    """Get the file extension for an export format."""
    extensions = {
        "markdown": ".md",
        "txt": ".txt",
        "json": ".json",
        "html": ".html",
    }
    return extensions.get(format, ".txt")

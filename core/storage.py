"""
Storage module for managing WritingSession data.
Handles saving, loading, and deleting session JSON files.
"""

import json
from pathlib import Path
from datetime import date, datetime
from typing import List

from .models import WritingSession

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SESSIONS_DIR = DATA_DIR / "sessions"

SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def get_session_path(sess: WritingSession) -> Path:
    """
    Return the filesystem path of the JSON file for a given WritingSession.
    Args:
        sess: WritingSession object
    Returns:
        Path to the session's JSON file
    """
    filename = f"{sess.session_date.isoformat()}-{sess.id}.json"
    return SESSIONS_DIR / filename

def session_to_dict(sess: WritingSession) -> dict:
    """
    Convert a WritingSession object to a dictionary.
    
    Args:
    sess: WritingSession object of a written session
    return:
    dict[Any, Any]: Dictionary representation of the WritingSession, converted from WritingSession object
    """
    return {
        "id": sess.id,
        "title": sess.title,  # <-- new
        "session_date": sess.session_date.isoformat(),
        "mode": sess.mode,
        "topic": sess.topic,
        "content": sess.content,
        "start_time": sess.start_time.isoformat(),
        "end_time": sess.end_time.isoformat() if sess.end_time else None,
        "duration_seconds": sess.duration_seconds,
        "char_count": sess.char_count,
        "word_count": sess.word_count,
    }


def dict_to_session(data: dict) -> WritingSession:
    """
    Convert a dictionary to a WritingSession object.
    Args:
        data: Dictionary representation of a WritingSession
    Returns:
        WritingSession object
    """
    sess_date = date.fromisoformat(data["session_date"])
    # for old JSON files without "title", default to the date string
    title = data.get("title") or sess_date.isoformat()

    return WritingSession(
        id=data["id"],
        title=title,  # <-- new
        session_date=sess_date,
        mode=data["mode"],
        topic=data.get("topic"),
        content=data["content"],
        start_time=datetime.fromisoformat(data["start_time"]),
        end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
        duration_seconds=data["duration_seconds"],
        char_count=data["char_count"],
        word_count=data["word_count"],
    )



def save_session(sess: WritingSession) -> None:
    """
    Save session as JSON file: data/sessions/YYYY-MM-DD-<id>.json
    Args:
        sess: WritingSession object to save
    """
    filename = f"{sess.session_date.isoformat()}-{sess.id}.json"
    path = SESSIONS_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(session_to_dict(sess), f, ensure_ascii=False, indent=2)


def delete_session(sess: WritingSession) -> None:
    """
    Delete the JSON file for a given WritingSession.
    Args:
        sess: WritingSession object to delete
    """
    path = get_session_path(sess)
    if path.exists():
        path.unlink()


def load_sessions_for_date(d: date) -> List[WritingSession]:
    """
    Load all sessions for a specific date.
    Args:
        d: date object representing the date to load sessions for
    Returns:
        List of WritingSession objects for the given date
    """
    prefix = d.isoformat() + "-"
    sessions: List[WritingSession] = []

    for path in SESSIONS_DIR.glob(f"{prefix}*.json"):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            sessions.append(dict_to_session(data))

    return sessions


def load_sessions_for_month(year: int, month: int) -> List[WritingSession]:
    """
    Load all sessions whose date is in the given month.
    Args:
        year: Year as integer
        month: Month as integer (1-12)
    Returns:
        List of WritingSession objects for the given month
    """
    sessions: List[WritingSession] = []
    for path in SESSIONS_DIR.glob("*.json"):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            sess = dict_to_session(data)
            if sess.session_date.year == year and sess.session_date.month == month:
                sessions.append(sess)
    return sessions


def load_all_sessions() -> List[WritingSession]:
    """
    Load all sessions stored in data/sessions.
    Returns:
        List of all WritingSession objects
    """
    sessions: List[WritingSession] = []

    for path in SESSIONS_DIR.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                sessions.append(dict_to_session(data))
        except Exception:
            # optionally log/print, but ignore broken files for now
            continue

    return sessions
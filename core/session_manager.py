"""
Manage writing sessions: start, update, and finish.

This module defines SessionManager, which owns the lifecycle
of the currently active writing session.
"""

import uuid
from datetime import datetime, date
from typing import Optional

from .models import WritingSession
from .utils import mixed_word_count
from .storage import save_session
from .streak_days import mark_day_completed


class SessionManager:
    """
    Manage the lifecycle of a single active writing session.

    This class is responsible for creating, updating, and finalizing
    WritingSession objects, and for persisting completed sessions.
    """
    def __init__(self):
        self.current_session: WritingSession | None = None

    def start_session(self, mode: str, topic: str | None) -> WritingSession:
        """
        Start a new writing session.

        Args:
            mode: Writing mode ("free" or "random_topic").
            topic: The writing topic, if applicable.

        Returns:
            The newly created WritingSession instance.
        """
        today = date.today()
        now = datetime.now()
        sess = WritingSession(
            id=str(uuid.uuid4()),
            title=today.isoformat(),  # default title = date
            session_date=today,
            mode=mode,
            topic=topic,
            content="",
            start_time=now,
            end_time=None,
            duration_seconds=0,
            char_count=0,
            word_count=0,
        )
        self.current_session = sess
        return sess

    def update_content(self, text: str) -> None:
        """
        Update the content of the current writing session.

        Args:
            text: The full text content entered so far.
        """
        if not self.current_session:
            return
        self.current_session.content = text
        self.current_session.char_count = len(text)
        self.current_session.word_count = mixed_word_count(text)

    def finish_session(self) -> Optional[WritingSession]:
        """
        Finish the current writing session and persist it.

        This method saves the session, marks the session date as completed,
        and clears the active session state.

        Returns:
            The completed WritingSession, or None if no session is active.
        """
        if not self.current_session:
            return None

        now = datetime.now()
        sess = self.current_session
        sess.end_time = now
        sess.duration_seconds = int((now - sess.start_time).total_seconds())

        text = sess.content
        sess.char_count = len(text)
        sess.word_count = mixed_word_count(text)

        save_session(sess)
        mark_day_completed(sess.session_date)

        self.current_session = None
        return sess

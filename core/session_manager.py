"""
Manage writing sessions: start, update, and finish.

This module defines SessionManager, which owns the lifecycle
of the currently active writing session.
"""

import json
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import Optional

from .models import WritingSession
from .utils import mixed_word_count
from .storage import save_session, session_to_dict, dict_to_session
from .streak_days import mark_day_completed
from .logging_config import get_logger

logger = get_logger("session_manager")

# Draft storage location
DRAFT_DIR = Path.home() / ".dailywriting" / "drafts"


class SessionManager:
    """
    Manage the lifecycle of a single active writing session.

    This class is responsible for creating, updating, and finalizing
    WritingSession objects, and for persisting completed sessions.
    Includes auto-save draft functionality for crash recovery.
    """
    def __init__(self):
        self.current_session: WritingSession | None = None
        self._draft_path: Path | None = None
        DRAFT_DIR.mkdir(parents=True, exist_ok=True)

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
        self._draft_path = DRAFT_DIR / f"draft-{sess.id}.json"
        logger.info("Session started: %s (mode=%s)", sess.id, mode)
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

    def update_title(self, title: str) -> None:
        """
        Update the title of the current writing session.

        Args:
            title: The new title for the session.
        """
        if not self.current_session:
            return
        self.current_session.title = title

    def save_draft(self) -> bool:
        """
        Save the current session as a draft for crash recovery.

        Returns:
            True if draft was saved successfully, False otherwise.
        """
        if not self.current_session or not self._draft_path:
            return False

        try:
            # Update duration before saving draft
            now = datetime.now()
            self.current_session.duration_seconds = int(
                (now - self.current_session.start_time).total_seconds()
            )

            with self._draft_path.open("w", encoding="utf-8") as f:
                json.dump(session_to_dict(self.current_session), f, ensure_ascii=False, indent=2)
            logger.debug("Draft saved: %s (%d words)", self.current_session.id, self.current_session.word_count)
            return True
        except OSError as e:
            logger.error("Failed to save draft: %s", e)
            return False

    def clear_draft(self) -> None:
        """Remove the draft file for the current session."""
        if self._draft_path and self._draft_path.exists():
            try:
                self._draft_path.unlink()
                logger.debug("Draft cleared: %s", self._draft_path.name)
            except OSError as e:
                logger.warning("Failed to clear draft: %s", e)
        self._draft_path = None

    def finish_session(self) -> Optional[WritingSession]:
        """
        Finish the current writing session and persist it.

        This method saves the session, marks the session date as completed,
        clears the draft, and clears the active session state.

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

        logger.info("Session finished: %s (%d words, %d seconds)",
                    sess.id, sess.word_count, sess.duration_seconds)

        # Clear the draft now that session is saved
        self.clear_draft()

        self.current_session = None
        return sess

    def cancel_session(self) -> None:
        """Cancel the current session without saving."""
        if self.current_session:
            logger.info("Session cancelled: %s", self.current_session.id)
            self.clear_draft()
            self.current_session = None

    @staticmethod
    def get_abandoned_drafts() -> list[WritingSession]:
        """
        Check for abandoned draft sessions from previous runs.

        Returns:
            List of WritingSession objects from abandoned drafts.
        """
        drafts = []
        if not DRAFT_DIR.exists():
            return drafts

        for path in DRAFT_DIR.glob("draft-*.json"):
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = dict_to_session(data)
                    drafts.append(session)
                    logger.info("Found abandoned draft: %s from %s",
                                session.id, session.session_date)
            except (json.JSONDecodeError, KeyError, ValueError, OSError) as e:
                logger.warning("Failed to load draft %s: %s", path.name, e)
                continue

        return drafts

    @staticmethod
    def delete_draft(session_id: str) -> bool:
        """
        Delete a specific draft by session ID.

        Args:
            session_id: The ID of the session whose draft should be deleted.

        Returns:
            True if draft was deleted, False if not found or error.
        """
        draft_path = DRAFT_DIR / f"draft-{session_id}.json"
        if draft_path.exists():
            try:
                draft_path.unlink()
                logger.info("Deleted abandoned draft: %s", session_id)
                return True
            except OSError as e:
                logger.error("Failed to delete draft %s: %s", session_id, e)
        return False

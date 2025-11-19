# core/models.py

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class WritingSession:
    id: str
    title: str             # new: editable title
    session_date: date
    mode: str              # "free" or "random_topic"
    topic: Optional[str]
    content: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    char_count: int
    word_count: int

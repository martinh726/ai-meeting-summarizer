from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MeetingStatus(str, Enum):
    """Lifecycle of a meeting as it moves through the processing pipeline."""

    uploaded = "uploaded"
    transcribing = "transcribing"
    summarizing = "summarizing"
    done = "done"
    failed = "failed"


class MeetingBase(SQLModel):
    title: str
    original_filename: str
    status: MeetingStatus = MeetingStatus.uploaded
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Meeting(MeetingBase, table=True):
    """Database table. Holds everything, including large fields the list view doesn't need."""

    id: int | None = Field(default=None, primary_key=True)
    file_path: str
    transcript: str | None = None
    summary: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    transcribe_seconds: float | None = None
    summarize_seconds: float | None = None


class MeetingRead(MeetingBase):
    """Lightweight shape returned by GET /meetings (no transcript or summary)."""

    id: int


class MeetingDetail(MeetingRead):
    """Full shape returned by GET /meetings/{id}."""

    transcript: str | None = None
    summary: dict[str, Any] | None = None
    transcribe_seconds: float | None = None
    summarize_seconds: float | None = None

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Status(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Status] = mapped_column(
        SAEnum(Status, name="task_status"), default=Status.todo
    )
    priority: Mapped[Priority] = mapped_column(
        SAEnum(Priority, name="task_priority"), default=Priority.medium
    )
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # comma-separated
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # pgvector column — 384 dims matches all-MiniLM-L6-v2
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(384), nullable=True)

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner: Mapped["User"] = relationship("User", back_populates="tasks")

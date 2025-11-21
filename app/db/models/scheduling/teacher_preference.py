from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.models.base import Base
from typing import Dict, Any
import uuid


class TeacherPreference(Base):
    """
    Stores teacher preferences (e.g., preferred days, avoid slots) as a JSON blob
    """
    __tablename__ = "teacher_preferences"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.teacher_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    preferences: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

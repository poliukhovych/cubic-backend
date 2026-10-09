from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Index, func, text
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        Index("uq_schedules_single_active", "is_active", unique=True, postgresql_where=text("is_active")),
    )

    schedule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

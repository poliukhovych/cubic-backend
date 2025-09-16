from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class Teacher(Base):
    __tablename__ = "teachers"
    __table_args__ = (
        UniqueConstraint("first_name", "last_name", "patronymic", name="uq_teachers_name"),
        UniqueConstraint("user_id", name="uq_teachers_user"),
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", onupdate="CASCADE", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(100), nullable=False)  # обов'язково для викладачів
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

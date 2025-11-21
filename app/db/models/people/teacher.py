from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
from app.db.models.common_enums import TeacherStatus, TeacherStatusEnum
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
    patronymic: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[TeacherStatus] = mapped_column(
        TeacherStatusEnum,
        nullable=False,
        default=TeacherStatus.PENDING
    )

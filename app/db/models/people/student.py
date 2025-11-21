from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
from app.db.models.common_enums import StudentStatus, StudentStatusEnum
import uuid


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_students_user"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", onupdate="CASCADE", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )

    group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.group_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[StudentStatus] = mapped_column(
        StudentStatusEnum,
        nullable=False,
        default=StudentStatus.PENDING
    )

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Date, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, func
from app.db.models.base import Base
import uuid


class Homework(Base):
    __tablename__ = "homework"
    __table_args__ = (
        Index("ix_homework_student", "student_id", "due_date"),
        Index("ix_homework_group", "group_id", "due_date"),
        Index("ix_homework_teacher", "teacher_id", "due_date"),
    )

    homework_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.student_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.course_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.group_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.teacher_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    text: Mapped[str] = mapped_column(String(2000), nullable=False)
    due_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    classroom_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class HomeworkFile(Base):
    __tablename__ = "homework_files"

    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    homework_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("homework.homework_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


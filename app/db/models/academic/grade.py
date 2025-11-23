from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, func
from app.db.models.base import Base
import uuid


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint("points >= 0", name="ck_grades_points"),
        Index("ix_grades_student_course", "student_id", "course_id"),
        Index("ix_grades_created_at", "created_at"),
    )

    grade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

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

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.teacher_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    points: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    max_points: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    classroom_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


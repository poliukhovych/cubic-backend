from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Date, Enum, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, func
from app.db.models.base import Base
import uuid
import enum


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("assignment_id", "student_id", "date", name="uq_attendance_assignment_student_date"),
        Index("ix_attendance_student", "student_id", "date"),
        Index("ix_attendance_assignment", "assignment_id", "date"),
    )

    attendance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assignments.assignment_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.student_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus, name="attendance_status_enum", create_type=True),
        nullable=False
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


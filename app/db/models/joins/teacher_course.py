from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class TeacherCourse(Base):
    __tablename__ = "teacher_course"
    __table_args__ = (
        UniqueConstraint("teacher_id", "course_id", name="pk_teacher_course"),
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.teacher_id", onupdate="CASCADE", ondelete="RESTRICT"),
        primary_key=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.course_id", onupdate="CASCADE", ondelete="RESTRICT"),
        primary_key=True,
    )

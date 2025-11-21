from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    UniqueConstraint,
    ForeignKey,
    Integer,
    CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
from app.db.models.common_enums import CourseFrequency, CourseFrequencyEnum
import uuid


class GroupCourse(Base):
    __tablename__ = "group_course"
    __table_args__ = (
        UniqueConstraint("group_id", "course_id", name="pk_group_course"),
        CheckConstraint("count_per_week > 0", name="ck_group_course_count")
    )

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.group_id", onupdate="CASCADE", ondelete="RESTRICT"),
        primary_key=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.course_id", onupdate="CASCADE", ondelete="RESTRICT"),
        primary_key=True,
    )

    count_per_week: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )

    frequency: Mapped[CourseFrequency] = mapped_column(
        CourseFrequencyEnum,
        nullable=False,
        server_default=CourseFrequency.WEEKLY.value
    )

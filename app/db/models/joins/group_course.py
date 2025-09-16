from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class GroupCourse(Base):
    __tablename__ = "group_course"
    __table_args__ = (
        UniqueConstraint("group_id", "course_id", name="pk_group_course"),
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

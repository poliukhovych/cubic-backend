from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class SubgroupConstraints(Base):
    __tablename__ = "subgroup_constraints"
    __table_args__ = (
        UniqueConstraint("schedule_id", "group_id", "course_id", name="pk_subgroup_constraints"),
        CheckConstraint("subgroups_count > 0", name="ck_subgroup_constraints_count"),
    )

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("schedules.schedule_id", onupdate="CASCADE", ondelete="RESTRICT"),
        primary_key=True,
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
    subgroups_count: Mapped[int] = mapped_column(Integer, nullable=False)

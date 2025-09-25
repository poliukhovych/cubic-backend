from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import SmallInteger, CheckConstraint, UniqueConstraint, Index, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid

CourseTypeEnum = Enum("lec", "prac", "lab", name="course_type", native_enum=True)


class Assignment(Base):
    __tablename__ = "assignments"
    __table_args__ = (
        UniqueConstraint("schedule_id", "timeslot_id", "group_id", "subgroup_no", name="uq_asg_subgroup_time"),
        UniqueConstraint("schedule_id", "timeslot_id", "teacher_id", name="uq_asg_teacher_time"),
        UniqueConstraint("schedule_id", "timeslot_id", "room_id", name="uq_asg_room_time"),
        Index("ix_asg_group_view", "schedule_id", "group_id", "subgroup_no", "timeslot_id"),
        Index("ix_asg_teacher_view", "schedule_id", "teacher_id", "timeslot_id"),
        Index("ix_asg_room_view", "schedule_id", "room_id", "timeslot_id"),
        CheckConstraint("subgroup_no > 0", name="ck_assignments_subgroup_no"),
    )

    assignment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("schedules.schedule_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    timeslot_id: Mapped[int] = mapped_column(
        ForeignKey("timeslots.timeslot_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.group_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    subgroup_no: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.course_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.teacher_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.room_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True,
    )

    course_type: Mapped[str] = mapped_column(CourseTypeEnum, nullable=False)  # 'lec' | 'prac' | 'lab'

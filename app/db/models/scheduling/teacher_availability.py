from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class TeacherAvailability(Base):
    """
    Join table linking Teachers to the Timeslots they are available for.
    """
    __tablename__ = "teacher_availability"
    __table_args__ = (
        UniqueConstraint("teacher_id", "timeslot_id", name="uq_teacher_timeslot"),
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.teacher_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    timeslot_id: Mapped[int] = mapped_column(
        ForeignKey("timeslots.timeslot_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    Integer,
    SmallInteger,
    UniqueConstraint,
    CheckConstraint,
    ForeignKey
)
from app.db.models.base import Base
from app.db.models.common_enums import (
    TimeslotFrequency,
    TimeslotFrequencyEnum
)


class Timeslot(Base):
    """
    Represents a single time block in a day.

    Includes a frequency column (all, odd, even) to support bi-weekly scheduling.
    """
    __tablename__ = "timeslots"
    __table_args__ = (
        UniqueConstraint("day", "lesson_id", "frequency", name="uq_timeslots_day_lesson_freq"),
        CheckConstraint("day BETWEEN 1 AND 7", name="ck_timeslots_day"),
    )

    timeslot_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.lesson_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    frequency: Mapped[TimeslotFrequency] = mapped_column(
        TimeslotFrequencyEnum,
        nullable=False,
        server_default=TimeslotFrequency.ALL.value
    )

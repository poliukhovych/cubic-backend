from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, SmallInteger, UniqueConstraint, CheckConstraint, ForeignKey
from app.db.models.base import Base


class Timeslot(Base):
    __tablename__ = "timeslots"
    __table_args__ = (
        UniqueConstraint("day", "lesson_id", name="uq_timeslots_day_lesson"),
        CheckConstraint("day BETWEEN 1 AND 7", name="ck_timeslots_day"),
    )

    timeslot_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.lesson_id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

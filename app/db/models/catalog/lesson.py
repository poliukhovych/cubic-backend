from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Time, CheckConstraint
from app.db.models.base import Base


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        CheckConstraint("lesson_id BETWEEN 1 AND 4", name="ck_lessons_id_range"),
        CheckConstraint("start_time < end_time", name="ck_lessons_time_order"),
    )

    lesson_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 1..4 вручну
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)

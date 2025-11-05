from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("duration > 0", name="ck_courses_duration"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # години

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_rooms_capacity"),
    )

    room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid


class GroupUnavailability(Base):
    """
    Join table linking Groups to the Timeslots they are UNAVAILABLE for.
    """
    __tablename__ = "group_unavailability"
    __table_args__ = (
        UniqueConstraint(
            "group_id", "timeslot_id", name="uq_group_timeslot"
        ),
    )

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.group_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    timeslot_id: Mapped[int] = mapped_column(
        ForeignKey("timeslots.timeslot_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

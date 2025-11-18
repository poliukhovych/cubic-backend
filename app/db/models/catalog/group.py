from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, CheckConstraint, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.base import Base
import uuid
import enum


class GroupType(str, enum.Enum):
    BACHELOR = "bachelor"
    MASTER = "master"


class Group(Base):
    """
    Represents a student group or a subgroup.

    Subgroups are modeled as regular groups with a 'parent_group_id'
    pointing to their parent.
    """
    __tablename__ = "groups"
    __table_args__ = (
        CheckConstraint("size > 0", name="ck_groups_size"),
        CheckConstraint("course >= 1 AND course <= 6", name="ck_groups_course"),
    )

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    type: Mapped[GroupType] = mapped_column(
        SQLEnum(GroupType, name="group_type_enum", create_type=True),
        nullable=False,
        server_default="bachelor"
    )
    course: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    parent_group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.group_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

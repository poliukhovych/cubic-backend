from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from app.db.models.base import Base
from app.db.models.people.user import UserRole
import uuid
import enum


class RegistrationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RegistrationRequest(Base):
    __tablename__ = "registration_requests"

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # From Google token
    google_sub: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Contact
    email: Mapped[str] = mapped_column(CITEXT(), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(100))

    # Requested role
    requested_role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role_enum", create_type=True), nullable=False
    )

    status: Mapped[RegistrationStatus] = mapped_column(
        SQLEnum(RegistrationStatus, name="registration_status_enum", create_type=True),
        nullable=False,
        default=RegistrationStatus.PENDING,
    )

    admin_note: Mapped[str | None] = mapped_column(Text())

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    decided_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

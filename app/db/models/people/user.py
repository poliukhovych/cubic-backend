from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from app.db.models.base import Base
import uuid


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("google_sub", name="uq_users_google_sub"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Google OIDC
    google_sub: Mapped[str] = mapped_column(String(255), nullable=False)

    # Contact Details
    email: Mapped[str] = mapped_column(CITEXT(), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(100))  # опційно для users

    # Statuses and Timestamps
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

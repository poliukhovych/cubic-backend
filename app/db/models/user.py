from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.db.models.base import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING_PROFILE = "pending_profile"
    PENDING_APPROVAL = "pending_approval"
    DISABLED = "disabled"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_PROFILE, nullable=False)
    
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    @property
    def is_teacher(self) -> bool:
        return self.role == UserRole.TEACHER
    
    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT
    
    @property
    def can_access_admin(self) -> bool:
        return self.is_admin and self.status == UserStatus.ACTIVE
    
    @property
    def can_access_teacher(self) -> bool:
        return (self.is_teacher or self.is_admin) and self.status == UserStatus.ACTIVE

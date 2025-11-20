from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, computed_field
from app.db.models.people.user import UserRole


class UserBase(BaseModel):
    email: str = Field(..., description="User email")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    patronymic: Optional[str] = Field(None, max_length=100, description="Middle name")
    role: UserRole = Field(..., description="User role: student, teacher, or admin")
    is_active: bool = Field(True, description="Whether the user is active")


class UserResponse(UserBase):
    user_id: uuid.UUID = Field(..., alias="userId", description="User ID")
    google_sub: str = Field(..., alias="googleSub", description="Google subject identifier")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., alias="firstName", min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., alias="lastName", min_length=1, max_length=100, description="Last name")
    patronymic: Optional[str] = Field(None, max_length=100, description="Middle name")
    role: UserRole = Field(..., description="User role: student, teacher, or admin")
    is_active: bool = Field(..., alias="isActive", description="Whether the user is active")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name field"""
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    class Config:
        from_attributes = True
        populate_by_name = True


class UserListResponse(BaseModel):
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")


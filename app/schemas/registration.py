import uuid
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, computed_field
from datetime import datetime
from app.db.models.people.user import UserRole


class RegistrationRequestOut(BaseModel):
    request_id: uuid.UUID = Field(..., alias="requestId")
    email: EmailStr = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    patronymic: Optional[str] = Field(None)
    requested_role: UserRole = Field(..., alias="requestedRole")
    status: Literal["pending", "approved", "rejected"] = Field(...)
    created_at: datetime = Field(..., alias="createdAt")
    admin_note: Optional[str] = Field(None, alias="adminNote")
    
    # Optional fields for frontend display
    group_id: Optional[uuid.UUID] = Field(None, alias="groupId")
    group_name: Optional[str] = Field(None, alias="groupName")
    subjects: Optional[list[str]] = Field(default_factory=list)
    
    @computed_field(alias="fullName")
    @property
    def full_name(self) -> str:
        """Computed field that combines first_name, patronymic, and last_name."""
        parts = [self.first_name]
        if self.patronymic:
            parts.append(self.patronymic)
        parts.append(self.last_name)
        return " ".join(parts)

    class Config:
        from_attributes = True
        populate_by_name = True


class UpdateRegistrationRequest(BaseModel):
    """Schema for updating registration request before approval."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="firstName")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="lastName")
    patronymic: Optional[str] = Field(None, max_length=100)
    requested_role: Optional[UserRole] = Field(None, alias="requestedRole")
    admin_note: Optional[str] = Field(None, alias="adminNote")
    group_id: Optional[uuid.UUID] = Field(None, alias="groupId")
    
    class Config:
        populate_by_name = True


class ApproveRegistrationRequest(BaseModel):
    role: Optional[UserRole] = Field(None, description="Override requested role if provided")
    admin_note: Optional[str] = None


class RejectRegistrationRequest(BaseModel):
    reason: Optional[str] = None


class RegistrationPendingResponse(BaseModel):
    pending: bool = True
    message: str = Field(default="Your registration request was submitted and is awaiting admin approval.")

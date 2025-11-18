import uuid
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field
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

    class Config:
        from_attributes = True
        populate_by_name = True


class ApproveRegistrationRequest(BaseModel):
    role: Optional[UserRole] = Field(None, description="Override requested role if provided")
    admin_note: Optional[str] = None


class RejectRegistrationRequest(BaseModel):
    reason: Optional[str] = None


class RegistrationPendingResponse(BaseModel):
    pending: bool = True
    message: str = Field(default="Your registration request was submitted and is awaiting admin approval.")

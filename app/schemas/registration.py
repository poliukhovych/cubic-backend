import uuid
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.db.models.people.user import UserRole


class RegistrationRequestOut(BaseModel):
    request_id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    requested_role: UserRole
    status: Literal["pending", "approved", "rejected"]
    created_at: datetime

    class Config:
        from_attributes = True


class ApproveRegistrationRequest(BaseModel):
    role: Optional[UserRole] = Field(None, description="Override requested role if provided")
    admin_note: Optional[str] = None


class RejectRegistrationRequest(BaseModel):
    reason: Optional[str] = None


class RegistrationPendingResponse(BaseModel):
    pending: bool = True
    message: str = Field(default="Your registration request was submitted and is awaiting admin approval.")

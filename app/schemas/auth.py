"""
Schemas for authentication and authorization
"""
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, computed_field
from app.db.models.people.user import UserRole


# ============= Request Schemas =============

class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth authentication"""
    id_token: str = Field(..., description="Google ID token from frontend")
    role: Optional[UserRole] = Field(None, description="User role (student/teacher) - only for first login")


class RoleSelectionRequest(BaseModel):
    """Request to set role for existing user without role"""
    role: UserRole = Field(..., description="Selected role: student or teacher")


class GoogleCallbackRequest(BaseModel):
    """Request body for Google OAuth callback with authorization code"""
    code: str = Field(..., description="Authorization code from Google OAuth")
    state: str = Field(..., description="CSRF state token")
    redirect_uri: str = Field(..., description="Redirect URI used in OAuth flow")


class GoogleRegisterRequest(BaseModel):
    """Request body for Google OAuth registration"""
    code: str = Field(..., description="Authorization code from Google OAuth")
    state: str = Field(..., description="CSRF state token")
    redirect_uri: str = Field(..., description="Redirect URI used in OAuth flow")
    role: UserRole = Field(..., description="User role (student or teacher)")


class GoogleLoginRequest(BaseModel):
    """Request body for Google OAuth login"""
    code: str = Field(..., description="Authorization code from Google OAuth")
    state: str = Field(..., description="CSRF state token")
    redirect_uri: str = Field(..., description="Redirect URI used in OAuth flow")


class AdminLoginRequest(BaseModel):
    """Request body for admin username/password login"""
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")


# ============= Response Schemas =============

class UserResponse(BaseModel):
    """User information in response"""
    user_id: uuid.UUID = Field(..., alias="userId")
    email: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    patronymic: Optional[str] = Field(None)
    role: UserRole = Field(...)
    is_active: bool = Field(..., alias="isActive")
    
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


class AuthResponse(BaseModel):
    """Response after successful authentication"""
    access_token: str = Field(..., alias="accessToken", description="JWT access token")
    token_type: str = Field(default="bearer", alias="tokenType", description="Token type")
    user: UserResponse = Field(..., description="User information")
    needs_role_selection: bool = Field(default=False, alias="needsRoleSelection", description="True if user needs to select role")
    
    class Config:
        populate_by_name = True


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: uuid.UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    role: UserRole = Field(..., description="User role")
    exp: int = Field(..., description="Token expiration timestamp")

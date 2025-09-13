from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

from app.db.models.user import UserRole, UserStatus


class User(BaseModel):
    """Simple user schema for dependencies"""
    id: str
    name: str
    email: str
    role: Optional[str] = None
    status: Optional[str] = None


class UserBase(BaseModel):
    """Базова схема користувача"""
    name: str
    email: EmailStr
    role: Optional[UserRole] = None
    status: UserStatus = UserStatus.PENDING_PROFILE


class UserCreate(UserBase):
    """Схема для створення користувача"""
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    """Схема для оновлення користувача"""
    name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Схема відповіді з інформацією про користувача"""
    id: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Розширена схема профілю користувача"""
    is_admin: bool
    is_teacher: bool
    is_student: bool
    can_access_admin: bool
    can_access_teacher: bool


class TokenData(BaseModel):
    """Схема даних токена"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class TokenResponse(BaseModel):
    """Схема відповіді з токеном"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LoginRequest(BaseModel):
    """Схема запиту на логін"""
    email: EmailStr
    password: Optional[str] = None 

class GoogleAuthRequest(BaseModel):
    """Схема запиту Google авторизації"""
    code: str
    state: Optional[str] = None


class AuthMeResponse(BaseModel):
    """Схема відповіді /auth/me"""
    user: UserResponse


class LogoutResponse(BaseModel):
    """Схема відповіді на логаут"""
    message: str = "Successfully logged out"


class ErrorResponse(BaseModel):
    """Схема відповіді з помилкою"""
    error: str
    detail: str
    status_code: int

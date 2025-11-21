from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import uuid

from app.services.user_service import UserService
from app.core.deps import get_user_service
from app.schemas.user import UserResponse, UserListResponse

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def get_all_users(
    user_service: UserService = Depends(get_user_service)
) -> UserListResponse:
    """Отримати всіх користувачів"""
    return await user_service.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Отримати користувача за ID"""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with id {user_id} not found"
        )
    return user


from fastapi import Request, Depends, HTTPException, status
from typing import AsyncGenerator

from app.services.course_service import CourseService
from app.services.teacher_service import TeacherService
from app.services.group_service import GroupService
from app.services.mock_auth_service import MockAuthService
from app.schemas.auth import User


def get_course_service(request: Request) -> CourseService:
    return request.app.state.course_service


def get_teacher_service(request: Request) -> TeacherService:
    return request.app.state.teacher_service


def get_group_service(request: Request) -> GroupService:
    return request.app.state.group_service


async def get_db() -> AsyncGenerator[None, None]:
    yield None


async def get_current_user(request: Request) -> User:
    try:
        user_data = getattr(request.state, 'user', None)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        auth_service = MockAuthService()
        user = await auth_service.get_user_by_id(user_data['id'])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return User(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

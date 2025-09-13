from fastapi import Request
from typing import AsyncGenerator

from app.services.course_service import CourseService
from app.services.teacher_service import TeacherService
from app.services.group_service import GroupService


def get_course_service(request: Request) -> CourseService:
    return request.app.state.course_service


def get_teacher_service(request: Request) -> TeacherService:
    return request.app.state.teacher_service


def get_group_service(request: Request) -> GroupService:
    return request.app.state.group_service


# Заглушка для get_db - поки що не використовується
async def get_db() -> AsyncGenerator[None, None]:
    """Заглушка для get_db - поки що не використовується"""
    yield None

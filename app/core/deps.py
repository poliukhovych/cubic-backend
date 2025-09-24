from fastapi import Request
from app.db.session import async_session_maker
from app.services.course_service import CourseService
from app.services.teacher_service import TeacherService
from app.services.group_service import GroupService


async def get_session():
    async with async_session_maker() as session:
        yield session


def get_course_service(request: Request) -> CourseService:
    return request.app.state.course_service


def get_teacher_service(request: Request) -> TeacherService:
    return request.app.state.teacher_service


def get_group_service(request: Request) -> GroupService:
    return request.app.state.group_service

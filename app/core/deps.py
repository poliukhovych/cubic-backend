from fastapi import Request, Depends
from app.db.session import async_session_maker
from app.services.course_service import CourseService
from app.services.teacher_service import TeacherService
from app.services.group_service import GroupService
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session():
    async with async_session_maker() as session:
        yield session


async def get_course_service(session: AsyncSession = Depends(get_session)) -> CourseService:
    return CourseService(session)


def get_teacher_service(request: Request) -> TeacherService:
    return request.app.state.teacher_service


def get_group_service(request: Request) -> GroupService:
    return request.app.state.group_service
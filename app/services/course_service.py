from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse


class CourseService:
    def __init__(self, session: AsyncSession):
        self._repository = CourseRepository(session)

    async def get_all_courses(self) -> List[CourseResponse]:
        courses = await self._repository.find_all()
        return [CourseResponse.model_validate(course) for course in courses]

    async def get_course_by_id(self, course_id: UUID) -> Optional[CourseResponse]:
        course = await self._repository.find_by_id(course_id)
        if course:
            return CourseResponse.model_validate(course)
        return None

    async def get_courses_by_teacher_id(self, teacher_id: UUID) -> List[CourseResponse]:
        courses = await self._repository.find_by_teacher_id(teacher_id)
        return [CourseResponse.model_validate(course) for course in courses]

    async def create_course(self, course_data: CourseCreate) -> CourseResponse:
        existing_course = await self._repository.find_by_name(course_data.name)
        if existing_course:
            raise ValueError(f"Курс з назвою '{course_data.name}' вже існує")
        
        course = await self._repository.create(
            name=course_data.name,
            duration=course_data.duration
        )
        return CourseResponse.model_validate(course)

    async def update_course(self, course_id: UUID, course_data: CourseUpdate) -> Optional[CourseResponse]:
        if not await self._repository.exists(course_id):
            return None
        
        if course_data.name is not None:
            existing_course = await self._repository.find_by_name(course_data.name)
            if existing_course and existing_course.course_id != course_id:
                raise ValueError(f"Курс з назвою '{course_data.name}' вже існує")
        
        updated_course = await self._repository.update(
            course_id=course_id,
            name=course_data.name,
            duration=course_data.duration
        )
        
        if updated_course:
            return CourseResponse.model_validate(updated_course)
        return None

    async def delete_course(self, course_id: UUID) -> bool:
        """Видалити курс"""
        return await self._repository.delete(course_id)

    async def course_exists(self, course_id: UUID) -> bool:
        """Перевірити, чи існує курс"""
        return await self._repository.exists(course_id)

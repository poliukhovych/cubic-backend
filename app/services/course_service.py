from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseListResponse
from app.utils.unset import UNSET


class CourseService:
    def __init__(self, repo: CourseRepository):
        self.repo = repo

    async def get_all_courses(self) -> CourseListResponse:
        courses = await self.repo.find_all()
        total = await self.repo.count()
        return CourseListResponse(
            courses=[CourseResponse.model_validate(course) for course in courses],
            total=total
        )

    async def get_course_by_id(self, course_id: UUID) -> Optional[CourseResponse]:
        course = await self.repo.find_by_id(course_id)
        if course:
            return CourseResponse.model_validate(course)
        return None

    async def get_courses_by_teacher_id(self, teacher_id: UUID) -> List[CourseResponse]:
        courses = await self.repo.find_by_teacher_id(teacher_id)
        return [CourseResponse.model_validate(course) for course in courses]

    async def create_course(self, course_data: CourseCreate) -> CourseResponse:
        existing_course = await self.repo.find_by_name(course_data.name)
        if existing_course:
            raise ValueError(f"A course with the name '{course_data.name}' already exists.")
        
        course = await self.repo.create(
            name=course_data.name,
            duration=course_data.duration
        )
        return CourseResponse.model_validate(course)

    async def update_course(self, course_id: UUID, course_data: CourseUpdate) -> Optional[CourseResponse]:
        if not await self.repo.exists(course_id):
            return None
        
        if course_data.name is not UNSET and course_data.name is not None:
            existing_course = await self.repo.find_by_name(course_data.name)
            if existing_course and existing_course.course_id != course_id:
                raise ValueError(f"A course with the name '{course_data.name}' already exists.")
        
        updated_course = await self.repo.update(
            course_id=course_id,
            name=course_data.name,
            duration=course_data.duration
        )
        
        if updated_course:
            return CourseResponse.model_validate(updated_course)
        return None

    async def delete_course(self, course_id: UUID) -> bool:
        return await self.repo.delete(course_id)

    async def course_exists(self, course_id: UUID) -> bool:
        return await self.repo.exists(course_id)

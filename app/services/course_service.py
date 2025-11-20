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
        
        # Build course responses with relationships
        course_responses = []
        for course in courses:
            group_ids = await self.repo.get_group_ids_for_course(course.course_id)
            teacher_ids = await self.repo.get_teacher_ids_for_course(course.course_id)
            
            course_dict = {
                "course_id": course.course_id,
                "name": course.name,
                "duration": course.duration,
                "group_ids": group_ids,
                "teacher_ids": teacher_ids
            }
            course_responses.append(CourseResponse.model_validate(course_dict))
        
        return CourseListResponse(courses=course_responses, total=total)

    async def get_course_by_id(self, course_id: UUID) -> Optional[CourseResponse]:
        course = await self.repo.find_by_id(course_id)
        if course:
            group_ids = await self.repo.get_group_ids_for_course(course.course_id)
            teacher_ids = await self.repo.get_teacher_ids_for_course(course.course_id)
            
            course_dict = {
                "course_id": course.course_id,
                "name": course.name,
                "duration": course.duration,
                "group_ids": group_ids,
                "teacher_ids": teacher_ids
            }
            return CourseResponse.model_validate(course_dict)
        return None

    async def get_courses_by_teacher_id(self, teacher_id: UUID) -> List[CourseResponse]:
        courses = await self.repo.find_by_teacher_id(teacher_id)
        
        course_responses = []
        for course in courses:
            group_ids = await self.repo.get_group_ids_for_course(course.course_id)
            teacher_ids = await self.repo.get_teacher_ids_for_course(course.course_id)
            
            course_dict = {
                "course_id": course.course_id,
                "name": course.name,
                "duration": course.duration,
                "group_ids": group_ids,
                "teacher_ids": teacher_ids
            }
            course_responses.append(CourseResponse.model_validate(course_dict))
        
        return course_responses

    async def create_course(self, course_data: CourseCreate) -> CourseResponse:
        existing_course = await self.repo.find_by_name(course_data.name)
        if existing_course:
            raise ValueError(f"A course with the name '{course_data.name}' already exists.")
        
        course = await self.repo.create(
            name=course_data.name,
            duration=course_data.duration
        )
        
        # Create relationships if provided
        if course_data.group_ids:
            await self.repo.create_group_course_links(course.course_id, course_data.group_ids)
        if course_data.teacher_ids:
            await self.repo.create_teacher_course_links(course.course_id, course_data.teacher_ids)
        
        # Get relationships
        group_ids = await self.repo.get_group_ids_for_course(course.course_id)
        teacher_ids = await self.repo.get_teacher_ids_for_course(course.course_id)
        
        course_dict = {
            "course_id": course.course_id,
            "name": course.name,
            "duration": course.duration,
            "group_ids": group_ids,
            "teacher_ids": teacher_ids
        }
        return CourseResponse.model_validate(course_dict)

    async def update_course(self, course_id: UUID, course_data: CourseUpdate) -> Optional[CourseResponse]:
        if not await self.repo.exists(course_id):
            return None
        
        if course_data.name is not UNSET and course_data.name is not None:
            existing_course = await self.repo.find_by_name(course_data.name)
            if existing_course and existing_course.course_id != course_id:
                raise ValueError(f"A course with the name '{course_data.name}' already exists.")
        
        updated_course = await self.repo.update(
            course_id=course_id,
            name=course_data.name if course_data.name is not UNSET else UNSET,
            duration=course_data.duration if course_data.duration is not UNSET else UNSET
        )
        
        if updated_course:
            # Update relationships if provided
            if course_data.group_ids is not UNSET:
                if course_data.group_ids:
                    await self.repo.create_group_course_links(updated_course.course_id, course_data.group_ids)
                else:
                    await self.repo.delete_group_course_links(updated_course.course_id)
            
            if course_data.teacher_ids is not UNSET:
                if course_data.teacher_ids:
                    await self.repo.create_teacher_course_links(updated_course.course_id, course_data.teacher_ids)
                else:
                    await self.repo.delete_teacher_course_links(updated_course.course_id)
            
            # Get relationships
            group_ids = await self.repo.get_group_ids_for_course(updated_course.course_id)
            teacher_ids = await self.repo.get_teacher_ids_for_course(updated_course.course_id)
            
            course_dict = {
                "course_id": updated_course.course_id,
                "name": updated_course.name,
                "duration": updated_course.duration,
                "group_ids": group_ids,
                "teacher_ids": teacher_ids
            }
            return CourseResponse.model_validate(course_dict)
        return None

    async def delete_course(self, course_id: UUID) -> bool:
        return await self.repo.delete(course_id)

    async def course_exists(self, course_id: UUID) -> bool:
        return await self.repo.exists(course_id)

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseListResponse
from app.utils.unset import UNSET


class CourseService:
    def __init__(self, repo: CourseRepository):
        self.repo = repo

    async def _to_responses(self, courses) -> List[CourseResponse]:
        group_ids, teacher_ids = await self.repo.get_relation_ids_for_courses(
            [c.course_id for c in courses]
        )
        counts = await self.repo.get_count_per_week_for_courses([c.course_id for c in courses])
        return [
            CourseResponse.model_validate({
                "course_id": c.course_id,
                "name": c.name,
                "duration": c.duration,
                "code": c.code,
                "group_ids": group_ids[c.course_id],
                "teacher_ids": teacher_ids[c.course_id],
                "count_per_week": counts[c.course_id],
            })
            for c in courses
        ]

    async def get_all_courses(self) -> CourseListResponse:
        courses = await self.repo.find_all()
        total = await self.repo.count()
        return CourseListResponse(courses=await self._to_responses(courses), total=total)

    async def get_course_by_id(self, course_id: UUID) -> Optional[CourseResponse]:
        course = await self.repo.find_by_id(course_id)
        if course:
            group_ids = await self.repo.get_group_ids_for_course(course.course_id)
            teacher_ids = await self.repo.get_teacher_ids_for_course(course.course_id)
            
            course_dict = {
                "course_id": course.course_id,
                "name": course.name,
                "duration": course.duration,
                "code": course.code,
                "group_ids": group_ids,
                "teacher_ids": teacher_ids,
                "count_per_week": (await self.repo.get_count_per_week_for_courses([course.course_id]))[course.course_id],
            }
            return CourseResponse.model_validate(course_dict)
        return None

    async def get_courses_by_teacher_id(self, teacher_id: UUID) -> List[CourseResponse]:
        courses = await self.repo.find_by_teacher_id(teacher_id)
        return await self._to_responses(courses)

    async def _clean_code(self, code, course_id: Optional[UUID] = None):
        """Blank code -> NULL (the column is unique, so "" would clash); duplicate code -> ValueError (400)."""
        if code is UNSET or code is None:
            return code
        code = code.strip() or None
        if code:
            existing = await self.repo.find_by_code(code)
            if existing and existing.course_id != course_id:
                raise ValueError(f"A course with the code '{code}' already exists.")
        return code

    async def create_course(self, course_data: CourseCreate) -> CourseResponse:
        existing_course = await self.repo.find_by_name(course_data.name)
        if existing_course:
            raise ValueError(f"A course with the name '{course_data.name}' already exists.")
        
        course = await self.repo.create(
            name=course_data.name,
            duration=course_data.duration,
            code=await self._clean_code(course_data.code)
        )
        
        # Create relationships if provided
        if course_data.group_ids:
            await self.repo.create_group_course_links(course.course_id, course_data.group_ids, course_data.count_per_week)
        if course_data.teacher_ids:
            await self.repo.create_teacher_course_links(course.course_id, course_data.teacher_ids)
        
        # Get relationships
        group_ids = await self.repo.get_group_ids_for_course(course.course_id)
        teacher_ids = await self.repo.get_teacher_ids_for_course(course.course_id)
        
        course_dict = {
            "course_id": course.course_id,
            "name": course.name,
            "duration": course.duration,
            "code": course.code,
            "group_ids": group_ids,
            "teacher_ids": teacher_ids,
            "count_per_week": course_data.count_per_week,
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
            duration=course_data.duration if course_data.duration is not UNSET else UNSET,
            code=await self._clean_code(course_data.code, course_id)
        )
        
        if updated_course:
            # Recreated links keep the current count unless a new one is given
            count_per_week = course_data.count_per_week
            if count_per_week is None:
                count_per_week = (await self.repo.get_count_per_week_for_courses([course_id]))[course_id]
            # Update relationships if provided
            if course_data.group_ids is not UNSET:
                if course_data.group_ids:
                    await self.repo.create_group_course_links(updated_course.course_id, course_data.group_ids, count_per_week)
                else:
                    await self.repo.delete_group_course_links(updated_course.course_id)
            elif course_data.count_per_week is not None:
                await self.repo.set_count_per_week(course_id, count_per_week)
            
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
                "code": updated_course.code,
                "group_ids": group_ids,
                "teacher_ids": teacher_ids,
                "count_per_week": count_per_week,
            }
            return CourseResponse.model_validate(course_dict)
        return None

    async def delete_course(self, course_id: UUID) -> bool:
        return await self.repo.delete(course_id)

    async def course_exists(self, course_id: UUID) -> bool:
        return await self.repo.exists(course_id)

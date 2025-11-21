from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.catalog.course import Course
from app.db.models.joins.teacher_course import TeacherCourse
from app.db.models.joins.group_course import GroupCourse
from app.utils.unset import UNSET


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Course]:
        stmt = select(Course).order_by(Course.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, course_id: UUID) -> Optional[Course]:
        stmt = select(Course).where(Course.course_id == course_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Optional[Course]:
        stmt = select(Course).where(Course.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_teacher_id(self, teacher_id: UUID) -> List[Course]:
        stmt = (
            select(Course)
            .join(TeacherCourse, TeacherCourse.course_id == Course.course_id)
            .where(TeacherCourse.teacher_id == teacher_id)
            .order_by(Course.name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, name: str, duration: int, code: Optional[str] = None) -> Course:
        obj = Course(name=name, duration=duration, code=code)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, course_id: UUID, name: Union[str, None, object] = UNSET, duration: Union[int, None, object] = UNSET, code: Union[str, None, object] = UNSET) -> Optional[Course]:
        update_data = {}
        if name is not UNSET:
            update_data["name"] = name
        if duration is not UNSET:
            update_data["duration"] = duration
        if code is not UNSET:
            update_data["code"] = code
        
        if not update_data:
            return await self.find_by_id(course_id)
        
        stmt = (
            update(Course)
            .where(Course.course_id == course_id)
            .values(**update_data)
            .returning(Course)
        )
        result = await self._session.execute(stmt)
        updated_course = result.scalar_one_or_none()
        
        if updated_course:
            await self._session.refresh(updated_course)
        
        return updated_course

    async def delete(self, course_id: UUID) -> bool:
        stmt = delete(Course).where(Course.course_id == course_id).returning(Course.course_id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    async def exists(self, course_id: UUID) -> bool:
        stmt = select(Course.course_id).where(Course.course_id == course_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        """Counts the total number of courses."""
        stmt = select(func.count(Course.course_id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def get_group_ids_for_course(self, course_id: UUID) -> List[UUID]:
        """Get all group IDs assigned to a course."""
        stmt = select(GroupCourse.group_id).where(GroupCourse.course_id == course_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_teacher_ids_for_course(self, course_id: UUID) -> List[UUID]:
        """Get all teacher IDs assigned to a course."""
        stmt = select(TeacherCourse.teacher_id).where(TeacherCourse.course_id == course_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def create_group_course_links(self, course_id: UUID, group_ids: List[UUID]):
        """Create GroupCourse links for a course."""
        # Ensure course_id is a UUID object
        if isinstance(course_id, str):
            course_id = UUID(course_id)
        
        # Delete existing links first and flush to ensure they're removed
        await self.delete_group_course_links(course_id)
        
        # If no groups to add, return early
        if not group_ids:
            return
        
        # Create new links - ensure all IDs are UUID objects
        links_to_add = []
        for group_id in group_ids:
            # Convert to UUID if it's a string
            if isinstance(group_id, str):
                group_id = UUID(group_id)
            links_to_add.append(GroupCourse(group_id=group_id, course_id=course_id))
        
        # Add all links at once
        self._session.add_all(links_to_add)
        await self._session.flush()
    
    async def create_teacher_course_links(self, course_id: UUID, teacher_ids: List[UUID]):
        """Create TeacherCourse links for a course."""
        # Ensure course_id is a UUID object
        if isinstance(course_id, str):
            course_id = UUID(course_id)
        
        # Delete existing links first and flush to ensure they're removed
        await self.delete_teacher_course_links(course_id)
        
        # If no teachers to add, return early
        if not teacher_ids:
            return
        
        # Create new links - ensure all IDs are UUID objects
        links_to_add = []
        for teacher_id in teacher_ids:
            # Convert to UUID if it's a string
            if isinstance(teacher_id, str):
                teacher_id = UUID(teacher_id)
            links_to_add.append(TeacherCourse(teacher_id=teacher_id, course_id=course_id))
        
        # Add all links at once
        self._session.add_all(links_to_add)
        await self._session.flush()
    
    async def delete_group_course_links(self, course_id: UUID):
        """Delete all GroupCourse links for a course."""
        # Ensure course_id is a UUID object
        if isinstance(course_id, str):
            course_id = UUID(course_id)
        stmt = delete(GroupCourse).where(GroupCourse.course_id == course_id)
        await self._session.execute(stmt)
        await self._session.flush()
    
    async def delete_teacher_course_links(self, course_id: UUID):
        """Delete all TeacherCourse links for a course."""
        # Ensure course_id is a UUID object
        if isinstance(course_id, str):
            course_id = UUID(course_id)
        stmt = delete(TeacherCourse).where(TeacherCourse.course_id == course_id)
        await self._session.execute(stmt)
        await self._session.flush()
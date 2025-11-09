from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.catalog.course import Course
from app.db.models.joins.teacher_course import TeacherCourse

_UNSET = object()


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

    async def create(self, name: str, duration: int) -> Course:
        obj = Course(name=name, duration=duration)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, course_id: UUID, name: Union[str, None, object] = _UNSET, duration: Union[int, None, object] = _UNSET) -> Optional[Course]:
        update_data = {}
        if name is not _UNSET:
            update_data["name"] = name
        if duration is not _UNSET:
            update_data["duration"] = duration
        
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

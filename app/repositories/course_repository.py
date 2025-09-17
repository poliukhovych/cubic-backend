from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.catalog.course import Course
from app.db.models.joins.teacher_course import TeacherCourse


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Course]:
        stmt = select(Course)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, course_id: UUID) -> Optional[Course]:
        stmt = select(Course).where(Course.course_id == course_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_teacher_id(self, teacher_id: UUID) -> List[Course]:
        stmt = (
            select(Course)
            .join(TeacherCourse, TeacherCourse.course_id == Course.course_id)
            .where(TeacherCourse.teacher_id == teacher_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, name: str, duration: int) -> Course:
        obj = Course(name=name, duration=duration)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def delete(self, course_id: UUID) -> bool:
        stmt = delete(Course).where(Course.course_id == course_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

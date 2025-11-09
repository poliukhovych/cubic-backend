from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.joins.teacher_course import TeacherCourse


class TeacherCourseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[TeacherCourse]:
        stmt = select(TeacherCourse).order_by(TeacherCourse.teacher_id, TeacherCourse.course_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_composite_key(
        self,
        teacher_id: UUID,
        course_id: UUID
    ) -> Optional[TeacherCourse]:
        stmt = select(TeacherCourse).where(
            TeacherCourse.teacher_id == teacher_id,
            TeacherCourse.course_id == course_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_teacher_id(self, teacher_id: UUID) -> List[TeacherCourse]:
        stmt = (
            select(TeacherCourse)
            .where(TeacherCourse.teacher_id == teacher_id)
            .order_by(TeacherCourse.course_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_course_id(self, course_id: UUID) -> List[TeacherCourse]:
        stmt = (
            select(TeacherCourse)
            .where(TeacherCourse.course_id == course_id)
            .order_by(TeacherCourse.teacher_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        teacher_id: UUID,
        course_id: UUID,
    ) -> TeacherCourse:
        obj = TeacherCourse(
            teacher_id=teacher_id,
            course_id=course_id,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def create_bulk(
        self,
        teacher_courses: List[dict]
    ) -> List[TeacherCourse]:
        objs = [
            TeacherCourse(
                teacher_id=tc["teacher_id"],
                course_id=tc["course_id"],
            )
            for tc in teacher_courses
        ]
        self._session.add_all(objs)
        await self._session.flush()
        for obj in objs:
            await self._session.refresh(obj)
        return objs

    async def delete(
        self,
        teacher_id: UUID,
        course_id: UUID
    ) -> bool:
        stmt = (
            delete(TeacherCourse)
            .where(
                TeacherCourse.teacher_id == teacher_id,
                TeacherCourse.course_id == course_id
            )
            .returning(TeacherCourse.teacher_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_by_teacher_id(self, teacher_id: UUID) -> int:
        stmt = (
            delete(TeacherCourse)
            .where(TeacherCourse.teacher_id == teacher_id)
            .returning(TeacherCourse.teacher_id)
        )
        result = await self._session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        return len(deleted_ids)

    async def delete_by_course_id(self, course_id: UUID) -> int:
        stmt = (
            delete(TeacherCourse)
            .where(TeacherCourse.course_id == course_id)
            .returning(TeacherCourse.course_id)
        )
        result = await self._session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        return len(deleted_ids)

    async def exists(
        self,
        teacher_id: UUID,
        course_id: UUID
    ) -> bool:
        stmt = select(TeacherCourse).where(
            TeacherCourse.teacher_id == teacher_id,
            TeacherCourse.course_id == course_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


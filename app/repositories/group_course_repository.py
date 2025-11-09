from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.joins.group_course import GroupCourse


class GroupCourseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[GroupCourse]:
        stmt = select(GroupCourse).order_by(GroupCourse.group_id, GroupCourse.course_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_composite_key(
        self,
        group_id: UUID,
        course_id: UUID
    ) -> Optional[GroupCourse]:
        stmt = select(GroupCourse).where(
            GroupCourse.group_id == group_id,
            GroupCourse.course_id == course_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_group_id(self, group_id: UUID) -> List[GroupCourse]:
        stmt = (
            select(GroupCourse)
            .where(GroupCourse.group_id == group_id)
            .order_by(GroupCourse.course_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_course_id(self, course_id: UUID) -> List[GroupCourse]:
        stmt = (
            select(GroupCourse)
            .where(GroupCourse.course_id == course_id)
            .order_by(GroupCourse.group_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        group_id: UUID,
        course_id: UUID,
    ) -> GroupCourse:
        obj = GroupCourse(
            group_id=group_id,
            course_id=course_id,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def create_bulk(
        self,
        group_courses: List[dict]
    ) -> List[GroupCourse]:
        objs = [
            GroupCourse(
                group_id=gc["group_id"],
                course_id=gc["course_id"],
            )
            for gc in group_courses
        ]
        self._session.add_all(objs)
        await self._session.flush()
        for obj in objs:
            await self._session.refresh(obj)
        return objs

    async def delete(
        self,
        group_id: UUID,
        course_id: UUID
    ) -> bool:
        stmt = (
            delete(GroupCourse)
            .where(
                GroupCourse.group_id == group_id,
                GroupCourse.course_id == course_id
            )
            .returning(GroupCourse.group_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_by_group_id(self, group_id: UUID) -> int:
        stmt = (
            delete(GroupCourse)
            .where(GroupCourse.group_id == group_id)
            .returning(GroupCourse.group_id)
        )
        result = await self._session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        return len(deleted_ids)

    async def delete_by_course_id(self, course_id: UUID) -> int:
        stmt = (
            delete(GroupCourse)
            .where(GroupCourse.course_id == course_id)
            .returning(GroupCourse.course_id)
        )
        result = await self._session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        return len(deleted_ids)

    async def exists(
        self,
        group_id: UUID,
        course_id: UUID
    ) -> bool:
        stmt = select(GroupCourse).where(
            GroupCourse.group_id == group_id,
            GroupCourse.course_id == course_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


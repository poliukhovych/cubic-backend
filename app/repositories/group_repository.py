from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.catalog.group import Group
from app.db.models.joins.group_course import GroupCourse
from app.db.models.joins.teacher_course import TeacherCourse


class GroupRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Group]:
        stmt = select(Group)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, group_id: UUID) -> Optional[Group]:
        stmt = select(Group).where(Group.group_id == group_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_teacher_id(self, teacher_id: UUID) -> List[Group]:
        stmt = (
            select(Group)
            .join(GroupCourse, GroupCourse.group_id == Group.group_id)
            .join(TeacherCourse, TeacherCourse.course_id == GroupCourse.course_id)
            .where(TeacherCourse.teacher_id == teacher_id)
            .distinct()
        )
        result = await self._session.execute(stmt)
        # When joins are involved, duplicates can appear; unique() is safe.
        return list(result.scalars().unique().all())

    async def create(self, name: str, size: int) -> Group:
        obj = Group(name=name, size=size)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def delete(self, group_id: UUID) -> bool:
        stmt = delete(Group).where(Group.group_id == group_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

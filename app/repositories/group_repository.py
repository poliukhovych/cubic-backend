from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.catalog.group import Group
from app.db.models.joins.group_course import GroupCourse
from app.db.models.joins.teacher_course import TeacherCourse
from app.utils.unset import UNSET


class GroupRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Group]:
        stmt = select(Group).order_by(Group.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, group_id: UUID) -> Optional[Group]:
        stmt = select(Group).where(Group.group_id == group_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Optional[Group]:
        stmt = select(Group).where(Group.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_teacher_id(self, teacher_id: UUID) -> List[Group]:
        stmt = (
            select(Group)
            .join(GroupCourse, GroupCourse.group_id == Group.group_id)
            .join(TeacherCourse, TeacherCourse.course_id == GroupCourse.course_id)
            .where(TeacherCourse.teacher_id == teacher_id)
            .distinct()
            .order_by(Group.name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())

    async def create(self, name: str, size: int) -> Group:
        obj = Group(name=name, size=size)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, group_id: UUID, name: Union[str, None, object] = UNSET, size: Union[int, None, object] = UNSET) -> Optional[Group]:
        update_data = {}
        if name is not UNSET:
            update_data["name"] = name
        if size is not UNSET:
            update_data["size"] = size
        
        if not update_data:
            return await self.find_by_id(group_id)
        
        stmt = (
            update(Group)
            .where(Group.group_id == group_id)
            .values(**update_data)
            .returning(Group)
        )
        result = await self._session.execute(stmt)
        updated_group = result.scalar_one_or_none()
        
        if updated_group:
            await self._session.refresh(updated_group)
        
        return updated_group

    async def delete(self, group_id: UUID) -> bool:
        stmt = delete(Group).where(Group.group_id == group_id).returning(Group.group_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        stmt = select(Group)
        result = await self._session.execute(stmt)
        return len(list(result.scalars().all()))

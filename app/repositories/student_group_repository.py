from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.joins.student_group import StudentGroup
from app.utils.unset import UNSET


class StudentGroupRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[StudentGroup]:
        stmt = select(StudentGroup).order_by(StudentGroup.student_id, StudentGroup.group_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_student_id(self, student_id: UUID) -> Optional[StudentGroup]:
        stmt = select(StudentGroup).where(StudentGroup.student_id == student_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all_by_group_id(self, group_id: UUID) -> List[StudentGroup]:
        stmt = (
            select(StudentGroup)
            .where(StudentGroup.group_id == group_id)
            .order_by(StudentGroup.student_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        student_id: UUID,
        group_id: UUID,
    ) -> StudentGroup:
        obj = StudentGroup(
            student_id=student_id,
            group_id=group_id,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def create_bulk(
        self,
        student_groups: List[dict]
    ) -> List[StudentGroup]:
        objs = [
            StudentGroup(
                student_id=sg["student_id"],
                group_id=sg["group_id"],
            )
            for sg in student_groups
        ]
        self._session.add_all(objs)
        await self._session.flush()
        for obj in objs:
            await self._session.refresh(obj)
        return objs

    async def update(
        self,
        student_id: UUID,
        *,
        group_id: Union[UUID, None, object] = UNSET,
    ) -> Optional[StudentGroup]:
        update_data = {}
        if group_id is not UNSET:
            update_data["group_id"] = group_id

        if not update_data:
            return await self.find_by_student_id(student_id)

        stmt = (
            update(StudentGroup)
            .where(StudentGroup.student_id == student_id)
            .values(**update_data)
            .returning(StudentGroup)
        )
        result = await self._session.execute(stmt)
        updated_student_group = result.scalar_one_or_none()

        if updated_student_group:
            await self._session.refresh(updated_student_group)

        return updated_student_group

    async def delete(self, student_id: UUID) -> bool:
        stmt = (
            delete(StudentGroup)
            .where(StudentGroup.student_id == student_id)
            .returning(StudentGroup.student_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_by_group_id(self, group_id: UUID) -> int:
        stmt = (
            delete(StudentGroup)
            .where(StudentGroup.group_id == group_id)
            .returning(StudentGroup.student_id)
        )
        result = await self._session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        return len(deleted_ids)

    async def exists(self, student_id: UUID) -> bool:
        stmt = select(StudentGroup.student_id).where(StudentGroup.student_id == student_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


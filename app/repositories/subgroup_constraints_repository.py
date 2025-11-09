from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.scheduling.subgroup_contraints import SubgroupConstraints
from app.utils.unset import UNSET


class SubgroupConstraintsRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[SubgroupConstraints]:
        stmt = select(SubgroupConstraints).order_by(
            SubgroupConstraints.schedule_id,
            SubgroupConstraints.group_id,
            SubgroupConstraints.course_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_composite_key(
        self,
        schedule_id: UUID,
        group_id: UUID,
        course_id: UUID
    ) -> Optional[SubgroupConstraints]:
        stmt = select(SubgroupConstraints).where(
            SubgroupConstraints.schedule_id == schedule_id,
            SubgroupConstraints.group_id == group_id,
            SubgroupConstraints.course_id == course_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_schedule_id(self, schedule_id: UUID) -> List[SubgroupConstraints]:
        stmt = (
            select(SubgroupConstraints)
            .where(SubgroupConstraints.schedule_id == schedule_id)
            .order_by(SubgroupConstraints.group_id, SubgroupConstraints.course_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_schedule_and_group(
        self,
        schedule_id: UUID,
        group_id: UUID
    ) -> List[SubgroupConstraints]:
        stmt = (
            select(SubgroupConstraints)
            .where(
                SubgroupConstraints.schedule_id == schedule_id,
                SubgroupConstraints.group_id == group_id
            )
            .order_by(SubgroupConstraints.course_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        schedule_id: UUID,
        group_id: UUID,
        course_id: UUID,
        subgroups_count: int,
    ) -> SubgroupConstraints:
        obj = SubgroupConstraints(
            schedule_id=schedule_id,
            group_id=group_id,
            course_id=course_id,
            subgroups_count=subgroups_count,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def create_bulk(
        self,
        constraints: List[dict]
    ) -> List[SubgroupConstraints]:
        objs = [
            SubgroupConstraints(
                schedule_id=c["schedule_id"],
                group_id=c["group_id"],
                course_id=c["course_id"],
                subgroups_count=c["subgroups_count"],
            )
            for c in constraints
        ]
        self._session.add_all(objs)
        await self._session.flush()
        for obj in objs:
            await self._session.refresh(obj)
        return objs

    async def update(
        self,
        schedule_id: UUID,
        group_id: UUID,
        course_id: UUID,
        *,
        subgroups_count: Union[int, None, object] = UNSET,
    ) -> Optional[SubgroupConstraints]:
        update_data = {}
        if subgroups_count is not UNSET:
            update_data["subgroups_count"] = subgroups_count

        if not update_data:
            return await self.find_by_composite_key(schedule_id, group_id, course_id)

        stmt = (
            update(SubgroupConstraints)
            .where(
                SubgroupConstraints.schedule_id == schedule_id,
                SubgroupConstraints.group_id == group_id,
                SubgroupConstraints.course_id == course_id
            )
            .values(**update_data)
            .returning(SubgroupConstraints)
        )
        result = await self._session.execute(stmt)
        updated_constraint = result.scalar_one_or_none()

        if updated_constraint:
            await self._session.refresh(updated_constraint)

        return updated_constraint

    async def delete(
        self,
        schedule_id: UUID,
        group_id: UUID,
        course_id: UUID
    ) -> bool:
        stmt = (
            delete(SubgroupConstraints)
            .where(
                SubgroupConstraints.schedule_id == schedule_id,
                SubgroupConstraints.group_id == group_id,
                SubgroupConstraints.course_id == course_id
            )
            .returning(SubgroupConstraints.schedule_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_by_schedule_id(self, schedule_id: UUID) -> int:
        stmt = (
            delete(SubgroupConstraints)
            .where(SubgroupConstraints.schedule_id == schedule_id)
            .returning(SubgroupConstraints.schedule_id)
        )
        result = await self._session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        return len(deleted_ids)

    async def exists(
        self,
        schedule_id: UUID,
        group_id: UUID,
        course_id: UUID
    ) -> bool:
        stmt = select(SubgroupConstraints).where(
            SubgroupConstraints.schedule_id == schedule_id,
            SubgroupConstraints.group_id == group_id,
            SubgroupConstraints.course_id == course_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


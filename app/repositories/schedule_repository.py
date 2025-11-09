from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.scheduling.schedule import Schedule
from app.utils.unset import UNSET


class ScheduleRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Schedule]:
        stmt = select(Schedule).order_by(Schedule.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, schedule_id: UUID) -> Optional[Schedule]:
        stmt = select(Schedule).where(Schedule.schedule_id == schedule_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_label(self, label: str) -> Optional[Schedule]:
        stmt = select(Schedule).where(Schedule.label == label)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, label: str) -> Schedule:
        obj = Schedule(label=label)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, schedule_id: UUID, label: Union[str, None, object] = UNSET) -> Optional[Schedule]:
        update_data = {}
        if label is not UNSET:
            update_data["label"] = label

        if not update_data:
            return await self.find_by_id(schedule_id)

        stmt = (
            update(Schedule)
            .where(Schedule.schedule_id == schedule_id)
            .values(**update_data)
            .returning(Schedule)
        )
        result = await self._session.execute(stmt)
        updated_schedule = result.scalar_one_or_none()

        if updated_schedule:
            await self._session.refresh(updated_schedule)

        return updated_schedule

    async def delete(self, schedule_id: UUID) -> bool:
        stmt = delete(Schedule).where(Schedule.schedule_id == schedule_id).returning(Schedule.schedule_id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    async def exists(self, schedule_id: UUID) -> bool:
        stmt = select(Schedule.schedule_id).where(Schedule.schedule_id == schedule_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

from typing import List, Optional, Union

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.scheduling.timeslot import Timeslot
from app.utils.unset import UNSET


class TimeslotRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Timeslot]:
        stmt = select(Timeslot).order_by(Timeslot.day, Timeslot.lesson_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, timeslot_id: int) -> Optional[Timeslot]:
        stmt = select(Timeslot).where(Timeslot.timeslot_id == timeslot_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_day(self, day: int) -> List[Timeslot]:
        stmt = (
            select(Timeslot)
            .where(Timeslot.day == day)
            .order_by(Timeslot.lesson_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_lesson_id(self, lesson_id: int) -> List[Timeslot]:
        stmt = (
            select(Timeslot)
            .where(Timeslot.lesson_id == lesson_id)
            .order_by(Timeslot.day)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_day_and_lesson(self, day: int, lesson_id: int) -> Optional[Timeslot]:
        stmt = select(Timeslot).where(
            Timeslot.day == day,
            Timeslot.lesson_id == lesson_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        day: int,
        lesson_id: int,
    ) -> Timeslot:
        obj = Timeslot(
            day=day,
            lesson_id=lesson_id,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(
        self,
        timeslot_id: int,
        *,
        day: Union[int, None, object] = UNSET,
        lesson_id: Union[int, None, object] = UNSET,
    ) -> Optional[Timeslot]:
        update_data = {}
        if day is not UNSET:
            update_data["day"] = day
        if lesson_id is not UNSET:
            update_data["lesson_id"] = lesson_id

        if not update_data:
            return await self.find_by_id(timeslot_id)

        stmt = (
            update(Timeslot)
            .where(Timeslot.timeslot_id == timeslot_id)
            .values(**update_data)
            .returning(Timeslot)
        )
        result = await self._session.execute(stmt)
        updated_timeslot = result.scalar_one_or_none()

        if updated_timeslot:
            await self._session.refresh(updated_timeslot)

        return updated_timeslot

    async def delete(self, timeslot_id: int) -> bool:
        stmt = delete(Timeslot).where(Timeslot.timeslot_id == timeslot_id).returning(Timeslot.timeslot_id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    async def exists(self, timeslot_id: int) -> bool:
        stmt = select(Timeslot.timeslot_id).where(Timeslot.timeslot_id == timeslot_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

from typing import List, Optional, Union
from datetime import time

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.catalog.lesson import Lesson

_UNSET = object()


class LessonRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Lesson]:
        stmt = select(Lesson).order_by(Lesson.lesson_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, lesson_id: int) -> Optional[Lesson]:
        stmt = select(Lesson).where(Lesson.lesson_id == lesson_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        lesson_id: int,
        start_time: time,
        end_time: time,
    ) -> Lesson:
        obj = Lesson(
            lesson_id=lesson_id,
            start_time=start_time,
            end_time=end_time,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(
        self,
        lesson_id: int,
        *,
        start_time: Union[time, None, object] = _UNSET,
        end_time: Union[time, None, object] = _UNSET,
    ) -> Optional[Lesson]:
        update_data = {}
        if start_time is not _UNSET:
            update_data["start_time"] = start_time
        if end_time is not _UNSET:
            update_data["end_time"] = end_time

        if not update_data:
            return await self.find_by_id(lesson_id)

        stmt = (
            update(Lesson)
            .where(Lesson.lesson_id == lesson_id)
            .values(**update_data)
            .returning(Lesson)
        )
        result = await self._session.execute(stmt)
        updated_lesson = result.scalar_one_or_none()

        if updated_lesson:
            await self._session.refresh(updated_lesson)

        return updated_lesson

    async def delete(self, lesson_id: int) -> bool:
        stmt = delete(Lesson).where(Lesson.lesson_id == lesson_id).returning(Lesson.lesson_id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    async def exists(self, lesson_id: int) -> bool:
        stmt = select(Lesson.lesson_id).where(Lesson.lesson_id == lesson_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


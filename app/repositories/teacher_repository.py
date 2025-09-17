from typing import List, Optional
import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.people.teacher import Teacher


class TeacherRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Teacher]:
        stmt = select(Teacher)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, teacher_id: uuid.UUID) -> Optional[Teacher]:
        stmt = select(Teacher).where(Teacher.teacher_id == teacher_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        first_name: str,
        last_name: str,
        patronymic: str,
        confirmed: bool = False,
        user_id: Optional[uuid.UUID] = None,
    ) -> Teacher:
        obj = Teacher(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            confirmed=confirmed,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def delete(self, teacher_id: uuid.UUID) -> bool:
        stmt = delete(Teacher).where(Teacher.teacher_id == teacher_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

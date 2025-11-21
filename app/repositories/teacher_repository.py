from typing import List, Optional, Union
import uuid

from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.people.teacher import Teacher
from app.utils.unset import UNSET


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

    async def find_by_user_id(self, user_id: uuid.UUID) -> Optional[Teacher]:
        stmt = select(Teacher).where(Teacher.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        first_name: str,
        last_name: str,
        patronymic: str,
        status: str = "pending",
        user_id: Optional[uuid.UUID] = None,
    ) -> Teacher:
        obj = Teacher(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            status=status,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(
        self,
        teacher_id: uuid.UUID,
        first_name: Union[str, None, object] = UNSET,
        last_name: Union[str, None, object] = UNSET,
        patronymic: Union[str, None, object] = UNSET,
        status: Union[str, None, object] = UNSET,
        user_id: Union[uuid.UUID, None, object] = UNSET,
    ) -> Optional[Teacher]:
        update_data = {}
        if first_name is not UNSET:
            update_data["first_name"] = first_name
        if last_name is not UNSET:
            update_data["last_name"] = last_name
        if patronymic is not UNSET:
            update_data["patronymic"] = patronymic
        if status is not UNSET:
            update_data["status"] = status
        if user_id is not UNSET:
            update_data["user_id"] = user_id

        if not update_data:
            return await self.find_by_id(teacher_id)

        stmt = (
            update(Teacher)
            .where(Teacher.teacher_id == teacher_id)
            .values(**update_data)
            .returning(Teacher)
        )
        result = await self._session.execute(stmt)
        teacher = result.scalar_one_or_none()
        if teacher:
            await self._session.refresh(teacher)
        return teacher

    async def delete(self, teacher_id: uuid.UUID) -> bool:
        stmt = delete(Teacher).where(Teacher.teacher_id == teacher_id).returning(Teacher.teacher_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def activate_teacher(self, teacher_id: uuid.UUID) -> Optional[Teacher]:
        return await self.update(teacher_id, status="active")

    async def deactivate_teacher(self, teacher_id: uuid.UUID) -> Optional[Teacher]:
        return await self.update(teacher_id, status="inactive")

    async def count(self) -> int:
        """Counts the total number of teachers."""
        stmt = select(func.count(Teacher.teacher_id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0

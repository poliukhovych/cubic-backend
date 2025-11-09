from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.people.admin import Admin

_UNSET = object()


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Admin]:
        stmt = select(Admin).order_by(Admin.last_name, Admin.first_name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, admin_id: UUID) -> Optional[Admin]:
        stmt = select(Admin).where(Admin.admin_id == admin_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_user_id(self, user_id: UUID) -> Optional[Admin]:
        stmt = select(Admin).where(Admin.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        first_name: str,
        last_name: str,
        patronymic: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> Admin:
        obj = Admin(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            user_id=user_id,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(
        self,
        admin_id: UUID,
        *,
        first_name: Union[str, None, object] = _UNSET,
        last_name: Union[str, None, object] = _UNSET,
        patronymic: Union[str, None, object] = _UNSET,
        user_id: Union[UUID, None, object] = _UNSET,
    ) -> Optional[Admin]:
        update_data = {}
        if first_name is not _UNSET:
            update_data["first_name"] = first_name
        if last_name is not _UNSET:
            update_data["last_name"] = last_name
        if patronymic is not _UNSET:
            update_data["patronymic"] = patronymic
        if user_id is not _UNSET:
            update_data["user_id"] = user_id

        if not update_data:
            return await self.find_by_id(admin_id)

        stmt = (
            update(Admin)
            .where(Admin.admin_id == admin_id)
            .values(**update_data)
            .returning(Admin)
        )
        result = await self._session.execute(stmt)
        admin = result.scalar_one_or_none()

        if admin:
            await self._session.refresh(admin)

        return admin

    async def delete(self, admin_id: UUID) -> bool:
        stmt = delete(Admin).where(Admin.admin_id == admin_id).returning(Admin.admin_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists(self, admin_id: UUID) -> bool:
        stmt = select(Admin.admin_id).where(Admin.admin_id == admin_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_user_id(self, user_id: UUID) -> bool:
        stmt = select(Admin.admin_id).where(Admin.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


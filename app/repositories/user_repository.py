from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.people.user import User, UserRole


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[User]:
        stmt = select(User).order_by(User.last_name, User.first_name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(User).where(User.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_google_sub(self, google_sub: str) -> Optional[User]:
        stmt = select(User).where(User.google_sub == google_sub)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_role(self, role: UserRole) -> List[User]:
        stmt = select(User).where(User.role == role).order_by(User.last_name, User.first_name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        google_sub: str,
        email: str,
        first_name: str,
        last_name: str,
        patronymic: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: bool = True,
    ) -> User:
        obj = User(
            google_sub=google_sub,
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            role=role,
            is_active=is_active,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(
        self,
        user_id: UUID,
        *,
        google_sub: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        patronymic: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[User]:
        update_data = {}
        if google_sub is not None:
            update_data["google_sub"] = google_sub
        if email is not None:
            update_data["email"] = email
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if patronymic is not None:
            update_data["patronymic"] = patronymic
        if role is not None:
            update_data["role"] = role
        if is_active is not None:
            update_data["is_active"] = is_active

        if not update_data:
            return await self.find_by_id(user_id)

        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(**update_data)
            .returning(User)
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            await self._session.refresh(user)

        return user

    async def delete(self, user_id: UUID) -> bool:
        stmt = delete(User).where(User.user_id == user_id).returning(User.user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists(self, user_id: UUID) -> bool:
        stmt = select(User.user_id).where(User.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_google_sub(self, google_sub: str) -> bool:
        stmt = select(User.user_id).where(User.google_sub == google_sub)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(User.user_id).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def update_role(self, user_id: UUID, role: UserRole) -> Optional[User]:
        return await self.update(user_id, role=role)

    async def activate_user(self, user_id: UUID) -> Optional[User]:
        return await self.update(user_id, is_active=True)

    async def deactivate_user(self, user_id: UUID) -> Optional[User]:
        return await self.update(user_id, is_active=False)


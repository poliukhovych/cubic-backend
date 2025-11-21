from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.catalog.room import Room
from app.utils.unset import UNSET


class RoomRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Room]:
        stmt = select(Room).order_by(Room.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, room_id: UUID) -> Optional[Room]:
        stmt = select(Room).where(Room.room_id == room_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Optional[Room]:
        stmt = select(Room).where(Room.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, name: str, capacity: int) -> Room:
        obj = Room(name=name, capacity=capacity)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(
        self,
        room_id: UUID,
        name: Union[str, None, object] = UNSET,
        capacity: Union[int, None, object] = UNSET
    ) -> Optional[Room]:
        update_data = {}
        if name is not UNSET:
            update_data["name"] = name
        if capacity is not UNSET:
            update_data["capacity"] = capacity
        
        if not update_data:
            return await self.find_by_id(room_id)
        
        stmt = (
            update(Room)
            .where(Room.room_id == room_id)
            .values(**update_data)
            .returning(Room)
        )
        result = await self._session.execute(stmt)
        updated_room = result.scalar_one_or_none()
        
        if updated_room:
            await self._session.refresh(updated_room)
        
        return updated_room

    async def delete(self, room_id: UUID) -> bool:
        stmt = delete(Room).where(Room.room_id == room_id).returning(Room.room_id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    async def exists(self, room_id: UUID) -> bool:
        stmt = select(Room.room_id).where(Room.room_id == room_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        """Counts the total number of rooms."""
        stmt = select(func.count(Room.room_id))
        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

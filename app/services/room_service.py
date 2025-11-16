import uuid
from typing import Optional

from fastapi import HTTPException, status

from app.repositories.room_repository import RoomRepository
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomListResponse
from app.utils.unset import UNSET


class RoomService:
    def __init__(self, repo: RoomRepository):
        self.repo = repo

    async def get_all_rooms(self) -> RoomListResponse:
        """Gets all rooms with pagination/total count."""
        rooms = await self.repo.find_all()
        total = await self.repo.count()
        room_responses = [RoomResponse.model_validate(room) for room in rooms]
        return RoomListResponse(rooms=room_responses, total=total)

    async def get_room_by_id(self, room_id: uuid.UUID) -> Optional[RoomResponse]:
        """Gets a single room by its ID."""
        room = await self.repo.find_by_id(room_id)
        if room:
            return RoomResponse.model_validate(room)
        return None

    async def get_room_by_name(self, name: str) -> Optional[RoomResponse]:
        """Gets a single room by its unique name."""
        room = await self.repo.find_by_name(name)
        if room:
            return RoomResponse.model_validate(room)
        return None

    async def create_room(self, room_data: RoomCreate) -> RoomResponse:
        existing_room = await self.repo.find_by_name(room_data.name)
        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Room with name '{room_data.name}' already exists."
            )

        room = await self.repo.create(
            name=room_data.name,
            capacity=room_data.capacity
        )

        return RoomResponse.model_validate(room)

    async def update(self, room_id: uuid.UUID, room_data: RoomUpdate) -> Optional[RoomResponse]:
        if room_data.name is not UNSET and room_data.name is not None:
            existing_room = await self.repo.find_by_name(room_data.name)
            # Check if the found room is a different room
            if existing_room and existing_room.room_id != room_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Room with name '{room_data.name}' already exists."
                )

        room = await self.repo.update(
            room_id=room_id,
            name=room_data.name,
            capacity=room_data.capacity
        )

        if room:
            return RoomResponse.model_validate(room)
        return None  # Room with room_id not found

    async def delete_room(self, room_id: uuid.UUID) -> bool:
        return await self.repo.delete(room_id)

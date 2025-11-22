from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from app.services.room_service import RoomService
from app.core.deps import get_room_service
from app.schemas.room import RoomResponse, RoomListResponse

router = APIRouter()


@router.get("/", response_model=RoomListResponse)
async def get_all_rooms(
    room_service: RoomService = Depends(get_room_service)
) -> RoomListResponse:
    """Отримати всі кімнати з повною інформацією."""
    return await room_service.get_all_rooms()


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room_by_id(
    room_id: UUID,
    room_service: RoomService = Depends(get_room_service)
) -> RoomResponse:
    """Отримати кімнату за ID з повною інформацією."""
    room = await room_service.get_room_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


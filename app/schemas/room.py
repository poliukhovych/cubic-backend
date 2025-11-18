import uuid
from typing import List, Union

from pydantic import BaseModel, Field

from app.utils.unset import UNSET


class RoomBase(BaseModel):
    """Base schema for room properties."""
    name: str = Field(..., min_length=1, max_length=100, description="Room name or number")
    capacity: int = Field(..., gt=0, description="Room capacity (must be > 0)")


class RoomCreate(RoomBase):
    """Schema for creating a new room."""
    pass


class RoomUpdate(BaseModel):
    """Schema for updating a room (PATCH) using the UNSET pattern."""
    name: Union[str, None, object] = Field(UNSET, min_length=1, max_length=100, description="New room name or number")
    capacity: Union[int, None, object] = Field(UNSET, gt=0, description="New room capacity (> 0)")


class RoomResponse(RoomBase):
    """Schema for returning room data from the API."""
    room_id: uuid.UUID = Field(..., alias="roomId", description="Room ID")

    class Config:
        """Pydantic config to allow ORM model mapping."""
        from_attributes = True
        populate_by_name = True


class RoomListResponse(BaseModel):
    """Schema for returning a paginated list of rooms."""
    rooms: List[RoomResponse] = Field(..., description="List of rooms")
    total: int = Field(..., description="Total number of rooms")
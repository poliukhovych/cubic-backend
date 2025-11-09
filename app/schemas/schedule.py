import uuid
from datetime import datetime
from typing import List, Union
from pydantic import BaseModel, Field

from app.schemas.assignment import AssignmentResponse
from app.utils.unset import UNSET 


class ScheduleBase(BaseModel):
    """Base schema for schedule properties."""
    label: str = Field(..., min_length=1, max_length=255, description="Schedule label")


class ScheduleCreate(ScheduleBase):
    """Schema for creating a new schedule log."""
    pass


class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule log (PATCH)."""
    label: Union[str, None, object] = Field(UNSET, min_length=1, max_length=255)


class ScheduleResponse(ScheduleBase):
    """Schema for returning schedule data from the API."""
    schedule_id: uuid.UUID = Field(..., description="Schedule ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic config to allow ORM model mapping."""
        from_attributes = True


class ScheduleListResponse(BaseModel):
    """Schema for returning a paginated list of schedules."""
    schedules: List[ScheduleResponse] = Field(..., description="List of schedules")
    total: int = Field(..., description="Total number of schedules")


class ScheduleGenerationResponse(BaseModel):
    """Response model for the schedule generation endpoint."""
    message: str = Field(..., description="Summary message")
    schedule: List[AssignmentResponse] = Field(..., description="List of generated assignments")

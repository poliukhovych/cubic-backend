from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import time

from app.db.models.common_enums import TimeslotFrequency


class LessonResponse(BaseModel):
    """Schema for lesson time information."""
    lesson_id: int = Field(..., alias="lessonId", description="Lesson number (1-4)")
    start_time: time = Field(..., alias="startTime", description="Lesson start time")
    end_time: time = Field(..., alias="endTime", description="Lesson end time")

    class Config:
        from_attributes = True
        populate_by_name = True


class TimeslotResponse(BaseModel):
    """Schema for timeslot information with full details."""
    timeslot_id: int = Field(..., alias="timeslotId", description="Timeslot ID")
    day: int = Field(..., description="Day of week (1=Monday, 7=Sunday)")
    frequency: TimeslotFrequency = Field(..., description="Frequency: all, odd, or even weeks")
    lesson: LessonResponse = Field(..., description="Lesson time information")

    class Config:
        from_attributes = True
        populate_by_name = True


class TimeslotListResponse(BaseModel):
    """Schema for returning a list of timeslots."""
    timeslots: List[TimeslotResponse] = Field(..., description="List of timeslots")
    total: int = Field(..., description="Total number of timeslots")


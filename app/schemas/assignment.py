import uuid
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.db.models.common_enums import CourseType


class MicroserviceAssignment(BaseModel):
    """
    Schema for an assignment object *from* the scheduling microservice.
    It does not contain schedule_id or assignment_id.
    """
    timeslot_id: int = Field(..., description="Timeslot ID")
    group_id: uuid.UUID = Field(..., description="Group ID")
    subgroup_no: int = Field(..., description="Subgroup number")
    course_id: uuid.UUID = Field(..., description="Course ID")
    teacher_id: uuid.UUID = Field(..., description="Teacher ID")
    room_id: Optional[uuid.UUID] = Field(None, description="Room ID (null for remote)")
    course_type: CourseType = Field(..., description="Type of class (lec, prac, lab)")


class AssignmentCreate(MicroserviceAssignment):
    """Schema for creating a new assignment in the database."""
    schedule_id: uuid.UUID = Field(..., description="Parent Schedule ID")


class AssignmentResponse(AssignmentCreate):
    """Schema for returning a full assignment from the API."""
    assignment_id: uuid.UUID = Field(..., description="Assignment ID")

    model_config = ConfigDict(from_attributes=True)

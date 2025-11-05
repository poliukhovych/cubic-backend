from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Course name")
    duration: int = Field(..., gt=0, description="Course duration in hours")


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Course name")
    duration: Optional[int] = Field(None, gt=0, description="Course duration in hours")


class CourseResponse(CourseBase):
    course_id: UUID = Field(..., description="Unique course identifier")
    
    class Config:
        from_attributes = True

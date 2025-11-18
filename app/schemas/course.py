from pydantic import BaseModel, Field
from typing import Optional, Union
from uuid import UUID
from app.utils.unset import UNSET


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Course name")
    duration: int = Field(..., gt=0, description="Course duration in hours")


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Union[str, None, object] = Field(UNSET, min_length=1, max_length=255, description="Course name")
    duration: Union[int, None, object] = Field(UNSET, gt=0, description="Course duration in hours")


class CourseResponse(CourseBase):
    course_id: UUID = Field(..., alias="courseId", description="Unique course identifier")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class CourseListResponse(BaseModel):
    courses: list[CourseResponse] = Field(..., description="List of courses")
    total: int = Field(..., description="Total number of courses")

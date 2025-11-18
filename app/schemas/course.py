from pydantic import BaseModel, Field
from typing import Optional, Union
from uuid import UUID
from app.utils.unset import UNSET


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Course name")
    code: Optional[str] = Field(None, max_length=50, description="Course code (e.g., CS101)")
    duration: int = Field(..., gt=0, description="Course duration in hours")


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Union[str, None, object] = Field(UNSET, min_length=1, max_length=255, description="Course name")
    code: Union[str, None, object] = Field(UNSET, max_length=50, description="Course code")
    duration: Union[int, None, object] = Field(UNSET, gt=0, description="Course duration in hours")


class CourseResponse(CourseBase):
    course_id: UUID = Field(..., alias="courseId", description="Unique course identifier")
    group_ids: list[UUID] = Field(default_factory=list, alias="groupIds", description="List of group IDs assigned to this course")
    teacher_ids: list[UUID] = Field(default_factory=list, alias="teacherIds", description="List of teacher IDs assigned to this course")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class CourseListResponse(BaseModel):
    courses: list[CourseResponse] = Field(..., description="List of courses")
    total: int = Field(..., description="Total number of courses")

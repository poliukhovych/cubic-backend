from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Назва курсу")
    duration: int = Field(..., gt=0, description="Тривалість курсу в годинах")


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Назва курсу")
    duration: Optional[int] = Field(None, gt=0, description="Тривалість курсу в годинах")


class CourseResponse(CourseBase):
    course_id: UUID = Field(..., description="Унікальний ідентифікатор курсу")
    
    class Config:
        from_attributes = True

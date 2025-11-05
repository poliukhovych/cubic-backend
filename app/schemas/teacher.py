from typing import Optional
import uuid
from pydantic import BaseModel, Field


class TeacherBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Surname")
    patronymic: str = Field(..., min_length=1, max_length=100, description="Middle name")
    confirmed: bool = Field(default=False, description="Is the teacher verified")


class TeacherCreate(TeacherBase):
    user_id: Optional[uuid.UUID] = Field(None, description="User ID(optionally)")


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Surname")
    patronymic: Optional[str] = Field(None, min_length=1, max_length=100, description="Middle name")
    confirmed: Optional[bool] = Field(None, description="Is the teacher verified?")
    user_id: Optional[uuid.UUID] = Field(None, description="User ID")


class TeacherResponse(TeacherBase):
    teacher_id: uuid.UUID = Field(..., description="Teacher ID")
    user_id: Optional[uuid.UUID] = Field(None, description="User ID")

    class Config:
        from_attributes = True


class TeacherListResponse(BaseModel):
    teachers: list[TeacherResponse] = Field(..., description="List of teachers")
    total: int = Field(..., description="Total number of teachers")

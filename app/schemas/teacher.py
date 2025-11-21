from typing import Optional, Union
import uuid
from pydantic import BaseModel, Field, computed_field
from app.utils.unset import UNSET


class TeacherBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Surname")
    patronymic: str = Field(..., min_length=1, max_length=100, description="Middle name")
    status: str = Field(default="pending", description="Teacher status: pending, active, or inactive")


class TeacherCreate(TeacherBase):
    user_id: Optional[uuid.UUID] = Field(None, description="User ID(optionally)")


class TeacherUpdate(BaseModel):
    first_name: Union[str, None, object] = Field(UNSET, min_length=1, max_length=100, description="Name")
    last_name: Union[str, None, object] = Field(UNSET, min_length=1, max_length=100, description="Surname")
    patronymic: Union[str, None, object] = Field(UNSET, min_length=1, max_length=100, description="Middle name")
    status: Union[str, None, object] = Field(UNSET, description="Teacher status: pending, active, or inactive")
    user_id: Union[uuid.UUID, None, object] = Field(UNSET, description="User ID")


class TeacherResponse(TeacherBase):
    teacher_id: uuid.UUID = Field(..., alias="teacherId", description="Teacher ID")
    user_id: Optional[uuid.UUID] = Field(None, alias="userId", description="User ID")
    first_name: str = Field(..., alias="firstName", min_length=1, max_length=100, description="Name")
    last_name: str = Field(..., alias="lastName", min_length=1, max_length=100, description="Surname")
    patronymic: str = Field(..., min_length=1, max_length=100, description="Middle name")
    status: str = Field(..., description="Teacher status: pending, active, or inactive")

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name field"""
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    class Config:
        from_attributes = True
        populate_by_name = True


class TeacherListResponse(BaseModel):
    teachers: list[TeacherResponse] = Field(..., description="List of teachers")
    total: int = Field(..., description="Total number of teachers")

import uuid
from typing import Union, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field
from app.utils.unset import UNSET


class StudentBase(BaseModel):
    """Base schema for student properties."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Student first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Student last name")
    patronymic: Optional[str] = Field(None, min_length=1, max_length=100, description="Student patronymic")
    status: str = Field(default="pending", description="Student status: pending, active, or inactive")


class StudentCreate(StudentBase):
    """Schema for creating a new student."""
    user_id: Optional[uuid.UUID] = Field(None, description="User ID (optional)")
    group_id: Optional[uuid.UUID] = Field(None, description="Group ID (optional)")


class StudentUpdate(BaseModel):
    """Schema for updating a student (PATCH)."""
    first_name: Union[str, None, object] = Field(UNSET, min_length=1, max_length=100, description="Student first name")
    last_name: Union[str, None, object] = Field(UNSET, min_length=1, max_length=100, description="Student last name")
    patronymic: Union[str, None, object] = Field(UNSET, min_length=1, max_length=100, description="Student patronymic")
    status: Union[str, None, object] = Field(UNSET, description="Student status: pending, active, or inactive")
    user_id: Union[uuid.UUID, None, object] = Field(UNSET, description="User ID")
    group_id: Union[uuid.UUID, None, object] = Field(UNSET, description="Group ID")


class StudentOut(BaseModel):
    """Schema for returning student data from the API."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    student_id: uuid.UUID = Field(..., alias="studentId")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    patronymic: str | None = Field(None)
    status: str = Field(..., description="Student status: pending, active, or inactive")
    group_id: uuid.UUID | None = Field(None, alias="groupId")
    user_id: uuid.UUID | None = Field(None, alias="userId")

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name field"""
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"


class StudentListResponse(BaseModel):
    """Schema for returning a paginated list of students."""
    students: list[StudentOut] = Field(..., description="List of students")
    total: int = Field(..., description="Total number of students")

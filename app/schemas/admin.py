import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, computed_field


class AdminStats(BaseModel):
    students_total: int = Field(..., alias="studentsTotal", description="Total number of students")
    students_confirmed: int = Field(..., alias="studentsConfirmed", description="Number of confirmed students")
    teachers_total: int = Field(..., alias="teachersTotal", description="Total number of teachers")
    teachers_confirmed: int = Field(..., alias="teachersConfirmed", description="Number of confirmed teachers")
    courses_total: int = Field(..., alias="coursesTotal", description="Total number of courses")
    
    class Config:
        populate_by_name = True


class AdminStudent(BaseModel):
    student_id: uuid.UUID = Field(..., alias="studentId")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    patronymic: Optional[str] = Field(None)
    confirmed: bool = Field(...)
    email: Optional[EmailStr] = Field(None)
    group_id: Optional[uuid.UUID] = Field(None, alias="groupId")

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name field"""
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminTeacher(BaseModel):
    teacher_id: uuid.UUID = Field(..., alias="teacherId")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    patronymic: Optional[str] = Field(None)
    confirmed: bool = Field(...)
    email: Optional[EmailStr] = Field(None)
    user_id: Optional[uuid.UUID] = Field(None, alias="userId")

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name field"""
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminStudentListResponse(BaseModel):
    students: list[AdminStudent]
    total: int


class AdminTeacherListResponse(BaseModel):
    teachers: list[AdminTeacher]
    total: int

import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class AdminStats(BaseModel):
    students_total: int = Field(..., description="Total number of students")
    students_confirmed: int = Field(..., description="Number of confirmed students")
    teachers_total: int = Field(..., description="Total number of teachers")
    teachers_confirmed: int = Field(..., description="Number of confirmed teachers")
    courses_total: int = Field(..., description="Total number of courses")


class AdminStudent(BaseModel):
    student_id: uuid.UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    confirmed: bool
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class AdminTeacher(BaseModel):
    teacher_id: uuid.UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    confirmed: bool
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class AdminStudentListResponse(BaseModel):
    students: list[AdminStudent]
    total: int


class AdminTeacherListResponse(BaseModel):
    teachers: list[AdminTeacher]
    total: int

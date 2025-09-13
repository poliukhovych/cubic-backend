from typing import Optional, Literal
from pydantic import BaseModel


class Teacher(BaseModel):
    id: str
    name: str
    email: str
    subjects: list[str]
    busy_windows: Optional[list[dict]] = None


class TeacherCreate(BaseModel):
    name: str
    email: str
    subjects: list[str]


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    subjects: Optional[list[str]] = None


class TeacherDetailedScheduleRequest(BaseModel):
    teacher_id: str


class TeacherDetailedScheduleResponse(BaseModel):
    teacherId: str 
    lessons: list[dict]  


class TeacherStats(BaseModel):
    students: int
    teachers: int
    courses: int

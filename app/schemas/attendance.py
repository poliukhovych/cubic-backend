import uuid
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, ConfigDict


class AttendanceStudent(BaseModel):
    """Schema for attendance student entry."""
    model_config = ConfigDict(populate_by_name=True)
    
    student_id: uuid.UUID = Field(..., description="Student ID")
    status: str = Field(..., description="Attendance status: present, absent, late")
    note: Optional[str] = Field(None, description="Optional note")


class AttendanceCreate(BaseModel):
    """Schema for creating attendance."""
    model_config = ConfigDict(populate_by_name=True)
    
    students: List[AttendanceStudent] = Field(..., description="List of students with attendance")
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")


class AttendanceResponse(BaseModel):
    """Schema for attendance response."""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(..., description="Attendance ID")
    assignmentId: str = Field(..., alias="assignmentId", description="Assignment ID")
    studentId: str = Field(..., alias="studentId", description="Student ID")
    date: str = Field(..., description="Date in ISO format")
    status: str = Field(..., description="Attendance status")
    note: Optional[str] = Field(None, description="Optional note")
    createdAt: str = Field(..., alias="createdAt", description="Creation date in ISO format")


class AttendanceListResponse(BaseModel):
    """Schema for attendance list response."""
    model_config = ConfigDict(populate_by_name=True)
    
    attendances: List[AttendanceResponse] = Field(..., description="List of attendance records")


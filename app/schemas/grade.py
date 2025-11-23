import uuid
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GradeItem(BaseModel):
    """Schema for a single grade item."""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(..., alias="id")
    subject: str = Field(..., description="Course name")
    points: float = Field(..., description="Grade points")
    max: Optional[float] = Field(None, description="Maximum points")
    comment: Optional[str] = Field(None, description="Grade comment")
    createdAt: str = Field(..., alias="createdAt", description="Creation date in ISO format")
    classroomUrl: Optional[str] = Field(None, alias="classroomUrl", description="Classroom URL")


class SubjectGrades(BaseModel):
    """Schema for grades grouped by subject."""
    model_config = ConfigDict(populate_by_name=True)
    
    subject: str = Field(..., description="Subject name")
    items: list[GradeItem] = Field(..., description="List of grade items")
    total: float = Field(..., description="Total points for the subject")


class StudentGradesResponse(BaseModel):
    """Schema for student grades response."""
    model_config = ConfigDict(populate_by_name=True)
    
    studentId: str = Field(..., alias="studentId", description="Student ID")
    subjects: list[SubjectGrades] = Field(..., description="List of subjects with grades")
    updatedAt: str = Field(..., alias="updatedAt", description="Last update date in ISO format")


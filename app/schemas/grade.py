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


class GradeCreate(BaseModel):
    """Schema for creating a grade."""
    model_config = ConfigDict(populate_by_name=True)
    
    student_id: uuid.UUID = Field(..., description="Student ID")
    course_id: uuid.UUID = Field(..., description="Course ID")
    assignment_id: Optional[uuid.UUID] = Field(None, description="Assignment ID (optional)")
    points: float = Field(..., description="Grade points")
    max_points: Optional[float] = Field(None, description="Maximum points")
    grade_type: Optional[str] = Field(None, description="Grade type: exam, test, homework, project")
    comment: Optional[str] = Field(None, description="Grade comment")
    classroom_url: Optional[str] = Field(None, description="Classroom URL")


class GradeResponse(BaseModel):
    """Schema for grade response."""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(..., description="Grade ID")
    student_id: str = Field(..., alias="studentId", description="Student ID")
    course_id: str = Field(..., alias="courseId", description="Course ID")
    teacher_id: str = Field(..., alias="teacherId", description="Teacher ID")
    points: float = Field(..., description="Grade points")
    max_points: Optional[float] = Field(None, alias="maxPoints", description="Maximum points")
    comment: Optional[str] = Field(None, description="Grade comment")
    classroom_url: Optional[str] = Field(None, alias="classroomUrl", description="Classroom URL")
    created_at: str = Field(..., alias="createdAt", description="Creation date in ISO format")


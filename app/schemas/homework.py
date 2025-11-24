import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class HomeworkFile(BaseModel):
    """Schema for a homework file."""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(..., alias="id")
    url: str = Field(..., description="File URL")
    title: Optional[str] = Field(None, description="File title")


class HomeworkTask(BaseModel):
    """Schema for a homework task."""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(..., alias="id")
    subject: str = Field(..., description="Course name")
    text: str = Field(..., description="Homework description")
    createdAt: str = Field(..., alias="createdAt", description="Creation date in ISO format")
    dueDate: str = Field(..., alias="dueDate", description="Due date in ISO format (YYYY-MM-DD)")
    groupId: str = Field(..., alias="groupId", description="Group ID")
    teacherId: str = Field(..., alias="teacherId", description="Teacher ID")
    done: bool = Field(..., description="Whether the homework is done")
    classroomUrl: Optional[str] = Field(None, alias="classroomUrl", description="Classroom URL")
    files: List[HomeworkFile] = Field(default_factory=list, description="List of attached files")


class StudentHomeworkResponse(BaseModel):
    """Schema for student homework response."""
    model_config = ConfigDict(populate_by_name=True)
    
    tasks: List[HomeworkTask] = Field(..., description="List of homework tasks")
    totalWeeks: int = Field(..., alias="totalWeeks", description="Maximum number of weeks")


class HomeworkAttachment(BaseModel):
    """Schema for homework attachment."""
    model_config = ConfigDict(populate_by_name=True)
    
    url: str = Field(..., description="File URL")
    title: Optional[str] = Field(None, description="File title")


class HomeworkCreate(BaseModel):
    """Schema for creating homework."""
    model_config = ConfigDict(populate_by_name=True)
    
    course_id: uuid.UUID = Field(..., description="Course ID")
    group_ids: List[uuid.UUID] = Field(..., description="List of group IDs")
    title: str = Field(..., description="Homework title")
    description: str = Field(..., description="Homework description")
    due_date: str = Field(..., description="Due date in ISO format (YYYY-MM-DD)")
    attachments: Optional[List[HomeworkAttachment]] = Field(None, description="List of attachments")


class HomeworkSubmissionCreate(BaseModel):
    """Schema for submitting homework."""
    model_config = ConfigDict(populate_by_name=True)
    
    content: str = Field(..., description="Submission content")
    attachments: Optional[List[HomeworkAttachment]] = Field(None, description="List of attachments")


class HomeworkSubmissionResponse(BaseModel):
    """Schema for homework submission response."""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(..., description="Submission ID")
    homeworkId: str = Field(..., alias="homeworkId", description="Homework ID")
    studentId: str = Field(..., alias="studentId", description="Student ID")
    content: str = Field(..., description="Submission content")
    submittedAt: str = Field(..., alias="submittedAt", description="Submission date in ISO format")
    grade: Optional[float] = Field(None, description="Grade")
    feedback: Optional[str] = Field(None, description="Feedback")
    files: List[HomeworkFile] = Field(default_factory=list, description="List of attached files")


class HomeworkSubmissionsResponse(BaseModel):
    """Schema for homework submissions response."""
    model_config = ConfigDict(populate_by_name=True)
    
    submissions: List[HomeworkSubmissionResponse] = Field(..., description="List of submissions")


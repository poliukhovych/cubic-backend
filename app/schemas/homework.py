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


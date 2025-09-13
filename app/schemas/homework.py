from typing import Optional
from pydantic import BaseModel


class HomeworkFile(BaseModel):
    id: str
    url: str
    title: Optional[str] = None


class HomeworkTask(BaseModel):
    id: str
    subject: str
    text: str
    createdAt: str  
    dueDate: str  
    groupId: str 
    teacherId: str  
    classroomUrl: str  
    files: Optional[list[HomeworkFile]] = None


class StudentHomeworkResponse(BaseModel):
    tasks: list[HomeworkTask]
    totalWeeks: int  

class HomeworkTaskCreate(BaseModel):
    subject: str
    text: str
    dueDate: str  
    groupId: str  
    teacherId: str  
    classroomUrl: str  
    files: Optional[list[HomeworkFile]] = None


class HomeworkTaskUpdate(BaseModel):
    subject: Optional[str] = None
    text: Optional[str] = None
    dueDate: Optional[str] = None   
    classroomUrl: Optional[str] = None  
    files: Optional[list[HomeworkFile]] = None

from typing import Optional
from pydantic import BaseModel


class Course(BaseModel):
    id: str
    code: str
    title: str
    groupIds: list[str] 
    teacherId: Optional[str] = None 


class CourseCreate(BaseModel):
    code: str
    title: str
    groupIds: list[str]  
    teacherId: Optional[str] = None  


class CourseUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    groupIds: Optional[list[str]] = None  
    teacherId: Optional[str] = None  

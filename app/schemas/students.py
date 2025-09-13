from typing import Optional, Literal
from pydantic import BaseModel


class Student(BaseModel):
    id: str
    name: str
    email: str
    groupId: str 
    subgroup: Optional[Literal["a", "b"]] = None


class Group(BaseModel):
    id: str
    name: str
    size: int


class StudentCreate(BaseModel):
    name: str
    email: str
    groupId: str 
    subgroup: Optional[Literal["a", "b"]] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    groupId: Optional[str] = None  
    subgroup: Optional[Literal["a", "b"]] = None


class GroupCreate(BaseModel):
    name: str
    size: int


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    size: Optional[int] = None

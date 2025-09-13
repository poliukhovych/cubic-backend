from typing import Literal, Optional
from pydantic import BaseModel


class AdminLog(BaseModel):
    id: str
    ts: str
    level: Literal["info", "warn", "error"]
    message: str


class ChangeItem(BaseModel):
    id: str
    ts: str  # ISO
    entity: Literal["schedule", "teacher", "course", "student"]
    action: Literal["created", "updated", "deleted"]
    title: str
    actor: str
    trend: Optional[list[int]] = None


class AdminStats(BaseModel):
    students: int
    teachers: int
    courses: int


class GlobalScheduleUpdate(BaseModel):
    pass  


class AdminChangeCreate(BaseModel):
    entity: Literal["schedule", "teacher", "course", "student"]
    action: Literal["created", "updated", "deleted"]
    title: str
    actor: str
    trend: Optional[list[int]] = None


class FacultyScheduleUpdate(BaseModel):
    level: Literal["bachelor", "master"]
    lessons: list[dict]   


class FacultyScheduleResponse(BaseModel):
    lessons: list[dict] 


class FacultyGroupsResponse(BaseModel):
    groups: list[str]
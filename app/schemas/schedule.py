from typing import Optional, Literal
from pydantic import BaseModel


class TimeSlot(BaseModel):
    start: str
    end: str


class GroupRef(BaseModel):
    id: str
    name: str
    subgroup: Optional[Literal["a", "b"]] = None


class Lesson(BaseModel):
    id: str
    weekday: Literal[1, 2, 3, 4, 5, 6, 7]
    time: TimeSlot
    subject: str
    location: Optional[str] = None
    group: GroupRef
    parity: Optional[Literal["any", "even", "odd"]] = "any"
    meetingUrl: Optional[str] = None  


class StudentSchedule(BaseModel):
    studentId: str  
    group: GroupRef
    lessons: list[Lesson]


class TeacherSchedule(BaseModel):
    teacherId: str  
    lessons: list[Lesson]


class FacultyLesson(BaseModel):
    id: str
    weekday: Literal[1, 2, 3, 4, 5, 6]
    pair: Literal[1, 2, 3, 4]
    parity: Literal["any", "even", "odd"]
    time: TimeSlot
    course: Literal[1, 2, 3, 4]
    level: Literal["bachelor", "master"]
    group: str
    speciality: Optional[str] = None
    subject: str
    teacher: str
    location: Optional[str] = None
    pinned: Optional[bool] = False


class FacultyScheduleRequest(BaseModel):
    level: Literal["bachelor", "master"]


class FacultyScheduleResponse(BaseModel):
    lessons: list[FacultyLesson]


class FacultyGroupsRequest(BaseModel):
    level: Literal["bachelor", "master"]


class FacultyGroupsResponse(BaseModel):
    groups: list[str]


class ScheduleUpdate(BaseModel):
    effective_from: str

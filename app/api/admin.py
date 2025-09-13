from typing import List
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import random

from app.schemas.admin import (
    AdminLog, ChangeItem, AdminStats, GlobalScheduleUpdate,
    AdminChangeCreate, FacultyScheduleUpdate
)
from app.schemas.teachers import Teacher, TeacherDetailedScheduleResponse
from app.schemas.students import Student, Group
from app.schemas.courses import Course
from app.schemas.schedule import FacultyScheduleResponse, FacultyGroupsResponse
from app.core.deps import get_current_user
from app.schemas.auth import User

router = APIRouter()


def generate_mock_teachers() -> List[Teacher]:
    return [
        Teacher(
            id="t1",
            name="Проф. Іваненко",
            email="ivan@uni.ua",
            subjects=["БД"]
        ),
        Teacher(
            id="t2",
            name="Доцент Петренко",
            email="petro@uni.ua",
            subjects=["ОПП", "ПП"]
        ),
    ]


def generate_mock_groups() -> List[Group]:
    return [
        Group(id="g1", name="КН-41", size=28),
        Group(id="g2", name="КН-42", size=27),
        Group(id="g3", name="КН-43", size=26),
    ]


def generate_mock_students() -> List[Student]:
    return [
        Student(
            id="s1",
            name="Андрій Сидоренко",
            email="andriy@uni.ua",
            groupId="g1"
        ),
        Student(
            id="s2",
            name="Марія Коваленко",
            email="maria@uni.ua",
            groupId="g1",
            subgroup="a"
        ),
        Student(
            id="s3",
            name="Ірина Василенко",
            email="iryna@uni.ua",
            groupId="g2"
        ),
        Student(
            id="s4",
            name="Олег Ткаченко",
            email="oleh@uni.ua",
            groupId="g3",
            subgroup="b"
        ),
    ]


def generate_mock_courses() -> List[Course]:
    return [
        Course(
            id="c1",
            code="DB101",
            title="Бази даних",
            groupIds=["g1", "g2"],
            teacherId="t1"
        ),
        Course(
            id="c2",
            code="CS201",
            title="Операційні системи",
            groupIds=["g2"],
            teacherId="t2"
        ),
        Course(
            id="c3",
            code="PR301",
            title="Проєктний практикум",
            groupIds=["g1", "g3"],
            teacherId="t2"
        ),
        Course(
            id="c4",
            code="ALG150",
            title="Алгоритми та структури даних",
            groupIds=["g3"],
            teacherId="t1"
        ),
    ]


def generate_mock_logs() -> List[AdminLog]:
    now = datetime.now().isoformat()
    return [
        AdminLog(
            id="l1",
            ts=now,
            level="info",
            message="System warmed up"
        ),
        AdminLog(
            id="l2",
            ts=now,
            level="warn",
            message="Cache miss for /courses"
        ),
        AdminLog(
            id="l3",
            ts=now,
            level="error",
            message="Teacher sync failed: timeout"
        ),
    ]


def generate_mock_changes() -> List[ChangeItem]:
    now = datetime.now()
    return [
        ChangeItem(
            id="ch1",
            ts=(now.timestamp() - 3600).isoformat(),
            entity="schedule",
            action="updated",
            title="Правка розкладу КН-41",
            actor="Admin",
            trend=[3, 6, 4, 8, 7, 9]
        ),
        ChangeItem(
            id="ch2",
            ts=(now.timestamp() - 7200).isoformat(),
            entity="teacher",
            action="updated",
            title="Оновлено e-mail викладача",
            actor="Admin",
            trend=[2, 2, 3, 3, 4, 5]
        ),
        ChangeItem(
            id="ch3",
            ts=(now.timestamp() - 12000).isoformat(),
            entity="student",
            action="created",
            title="Додано студента",
            actor="Admin",
            trend=[1, 2, 2, 3, 4, 4]
        ),
        ChangeItem(
            id="ch4",
            ts=(now.timestamp() - 25000).isoformat(),
            entity="course",
            action="deleted",
            title="Видалено дубль курсу",
            actor="Admin",
            trend=[9, 7, 5, 6, 4, 3]
        ),
        ChangeItem(
            id="ch5",
            ts=(now.timestamp() - 36000).isoformat(),
            entity="schedule",
            action="updated",
            title="Перенесено пару",
            actor="Admin",
            trend=[5, 6, 5, 7, 6, 7]
        ),
        ChangeItem(
            id="ch6",
            ts=(now.timestamp() - 48000).isoformat(),
            entity="teacher",
            action="created",
            title="Додано викладача",
            actor="Admin",
            trend=[0, 1, 2, 4, 6, 8]
        ),
    ]


def generate_mock_faculty_lessons(level: str) -> List[dict]:
    lessons = []
    subjects = ["Математика", "ОПП", "Алгоритми", "БД", "Веб-технології"]
    teachers = ["Проф. Іваненко", "Доцент Петренко"]
    groups = ["КН-41", "КН-42", "КН-43", "ПМ-41", "ІНФ-42"]
    
    for i in range(10): 
        lesson = {
            "id": f"lesson_{i}",
            "weekday": random.randint(1, 6),
            "pair": random.randint(1, 4),
            "parity": random.choice(["any", "even", "odd"]),
            "time": {
                "start": f"{8 + random.randint(0, 8)}:{random.choice(['00', '30'])}",
                "end": f"{9 + random.randint(0, 8)}:{random.choice(['35', '05'])}"
            },
            "course": random.randint(1, 4),
            "level": level,
            "group": random.choice(groups),
            "subject": random.choice(subjects),
            "teacher": random.choice(teachers),
            "location": f"ауд. {random.randint(100, 600)}",
            "pinned": False
        }
        lessons.append(lesson)
    
    return lessons


@router.get("/teachers", response_model=List[Teacher])
async def fetch_teachers(current_user: User = Depends(get_current_user)):
    return generate_mock_teachers()


@router.get("/teachers/{teacherId}/schedule", response_model=TeacherDetailedScheduleResponse)
async def fetch_teacher_detailed_schedule(
    teacherId: str,
    current_user: User = Depends(get_current_user)
):
    return TeacherDetailedScheduleResponse(
        teacherId=teacherId,   
        lessons=[
            {
                "id": "lesson_1",
                "weekday": 1,
                "time": {"start": "10:00", "end": "11:35"},
                "subject": "БД",
                "location": "107",
                "group": {"id": "g1", "name": "КН-41"}
            }
        ]
    )


@router.post("/schedule/update-global")
async def update_global_schedule(
    update: GlobalScheduleUpdate,
    current_user: User = Depends(get_current_user)
):
    return {"ok": True}


@router.get("/stats", response_model=AdminStats)
async def fetch_admin_stats(current_user: User = Depends(get_current_user)):
    return AdminStats(students=55, teachers=69, courses=14)


@router.get("/logs", response_model=List[AdminLog])
async def fetch_admin_logs(current_user: User = Depends(get_current_user)):
    return generate_mock_logs()


@router.post("/changes")
async def push_admin_change(
    change: AdminChangeCreate,
    current_user: User = Depends(get_current_user)
):
    return {"ok": True}


@router.get("/changes", response_model=List[ChangeItem])
async def fetch_change_history(
    limit: int = 6,
    current_user: User = Depends(get_current_user)
):
    changes = generate_mock_changes()
    return changes[:limit]


@router.get("/faculty-schedule/{level}", response_model=FacultyScheduleResponse)
async def fetch_faculty_schedule(
    level: str,
    current_user: User = Depends(get_current_user)
):
    if level not in ["bachelor", "master"]:
        raise HTTPException(status_code=400, detail="Level must be 'bachelor' or 'master'")
    
    lessons = generate_mock_faculty_lessons(level)
    return FacultyScheduleResponse(lessons=lessons)


@router.post("/faculty-schedule/{level}")
async def save_faculty_schedule(
    level: str,
    update: FacultyScheduleUpdate,
    current_user: User = Depends(get_current_user)
):
    if level not in ["bachelor", "master"]:
        raise HTTPException(status_code=400, detail="Level must be 'bachelor' or 'master'")
    
   
    return {"ok": True}


@router.get("/faculty-groups/{level}", response_model=FacultyGroupsResponse)
async def fetch_faculty_groups(
    level: str,
    current_user: User = Depends(get_current_user)
):
    if level not in ["bachelor", "master"]:
        raise HTTPException(status_code=400, detail="Level must be 'bachelor' or 'master'")
    
    groups = ["КН-41", "КН-42", "КН-43", "ПМ-41", "ІНФ-42"]
    return FacultyGroupsResponse(groups=groups)


@router.get("/groups", response_model=List[Group])
async def fetch_admin_groups(current_user: User = Depends(get_current_user)):
    return generate_mock_groups()


@router.get("/students", response_model=List[Student])
async def fetch_admin_students(current_user: User = Depends(get_current_user)):
    return generate_mock_students()


@router.get("/courses", response_model=List[Course])
async def fetch_admin_courses(current_user: User = Depends(get_current_user)):
    return generate_mock_courses()

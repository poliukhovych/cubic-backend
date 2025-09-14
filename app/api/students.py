from typing import List
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random

from app.schemas.schedule import StudentSchedule
from app.schemas.homework import StudentHomeworkResponse, HomeworkTask, HomeworkFile

router = APIRouter()


def generate_mock_student_schedule(student_id: str) -> StudentSchedule:
    group = {"id": "g1", "name": "КН-41", "subgroup": "a"}
    
    pairs = {
        1: {"start": "08:30", "end": "10:05"},
        2: {"start": "10:25", "end": "12:00"},
        3: {"start": "12:10", "end": "13:45"},
        4: {"start": "14:00", "end": "15:35"},
        5: {"start": "15:45", "end": "17:20"},
    }
    
    lessons = [
        {
            "id": "l1",
            "weekday": 1,
            "time": pairs[1],
            "subject": "Математика",
            "location": "ауд. 204",
            "group": group,
            "parity": "any",
            "meetingUrl": "https://meet.google.com/abc-defg-hij"
        },
        {
            "id": "l2",
            "weekday": 1,
            "time": pairs[2],
            "subject": "ОПП",
            "location": "ауд. 312",
            "group": group,
            "parity": "even",
            "meetingUrl": "https://zoom.us/j/9991112223"
        },
        {
            "id": "l3",
            "weekday": 1,
            "time": pairs[3],
            "subject": "Алгоритми і структури даних",
            "location": "ауд. 221",
            "group": group,
            "parity": "odd",
            "meetingUrl": "https://meet.google.com/kln-opqr-stu"
        },
        {
            "id": "l4",
            "weekday": 2,
            "time": pairs[2],
            "subject": "Бази даних",
            "location": "ауд. 107",
            "group": group,
            "parity": "any",
            "meetingUrl": "https://meet.google.com/db1-xyza-zzz"
        },
        {
            "id": "l5",
            "weekday": 3,
            "time": pairs[1],
            "subject": "Теорія ймовірностей",
            "location": "ауд. 210",
            "group": group,
            "parity": "any",
            "meetingUrl": "https://meet.google.com/prob-222-333"
        },
        {
            "id": "l6",
            "weekday": 4,
            "time": pairs[2],
            "subject": "Математика",
            "location": "ауд. 204",
            "group": group,
            "parity": "any",
            "meetingUrl": "https://meet.google.com/math-666-777"
        },
        {
            "id": "l7",
            "weekday": 5,
            "time": pairs[1],
            "subject": "Бази даних (лаб.)",
            "location": "лаб. 2-07",
            "group": group,
            "parity": "even",
            "meetingUrl": "https://meet.google.com/dbl-222-111"
        },
        {
            "id": "l8",
            "weekday": 6,
            "time": pairs[2],
            "subject": "Англійська мова (розмовна)",
            "location": "ауд. 509",
            "group": group,
            "parity": "any",
            "meetingUrl": "https://zoom.us/j/1112223334"
        }
    ]
    
    return StudentSchedule(
        studentId=student_id, 
        group=group,
        lessons=lessons
    )


def generate_mock_homework(student_id: str) -> StudentHomeworkResponse:
    today = datetime.now()
    
    def make_date(offset_days: int) -> str:
        date = today + timedelta(days=offset_days)
        return date.strftime("%Y-%m-%d")
    
    tasks = [
        HomeworkTask(
            id="hw1",
            subject="БД",
            text="Нормалізувати схему до 3НФ. Зверніть увагу на аномалії вставки/оновлення/видалення та наведіть приклади.",
            createdAt=datetime.now().isoformat(),  
            dueDate=make_date(-4),  
            groupId="g1",  
            teacherId="t1",  
            classroomUrl="https://classroom.google.com/c/ABCD1234/a/XYZ111", 
            files=[
                HomeworkFile(
                    id="f1",
                    url="https://drive.google.com/file/d/xyz/view",
                    title="Приклад"
                )
            ]
        ),
        HomeworkTask(
            id="hw2",
            subject="ОПП",
            text="Реалізувати патерн Observer",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(-3),
            groupId="g1",
            teacherId="t2",
            classroomUrl="https://classroom.google.com/c/EFGH5678/a/XYZ222"
        ),
        HomeworkTask(
            id="hw3",
            subject="ОПП",
            text="Реалізувати патерн KISS",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(7),
            groupId="g1",
            teacherId="t2",
            classroomUrl="https://classroom.google.com/c/EFGH5678/a/XYZ222"
        ),
        HomeworkTask(
            id="hw4",
            subject="Алгоритми",
            text="ДП: мінімальна вартість шляху по матриці. Реалізація + аналіз складності.",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(13),
            groupId="g1",
            teacherId="t3",
            classroomUrl="https://classroom.google.com/c/ALGO1/a/A1"
        ),
        HomeworkTask(
            id="hw5",
            subject="Веб-технології",
            text="Сторінка з формою входу: валідація, анімації, адаптив, ARIA-атрибути.",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(15),
            groupId="g1",
            teacherId="t4",
            classroomUrl="https://classroom.google.com/c/WEB1/a/W1"
        ),
        HomeworkTask(
            id="hw6",
            subject="Комп'ютерні мережі",
            text="Побудувати таблицю маршрутизації для заданої топології. Пояснити алгоритм SPF.",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(20),
            groupId="g1",
            teacherId="t5",
            classroomUrl="https://classroom.google.com/c/NET1/a/N1"
        ),
        HomeworkTask(
            id="hw7",
            subject="Фізика",
            text="Розв'язати 5 задач з оптики. Коротко описати модель і припущення.",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(23),
            groupId="g1",
            teacherId="t6",
            classroomUrl="https://classroom.google.com/c/PHY1/a/P1"
        ),
        HomeworkTask(
            id="hw8",
            subject="Теорія ймовірностей",
            text="Закон великих чисел: довести формулювання Чебишева на прикладі.",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(28),
            groupId="g1",
            teacherId="t7",
            classroomUrl="https://classroom.google.com/c/PROB1/a/PR1"
        ),
        HomeworkTask(
            id="hw9",
            subject="Операційні системи",
            text="Порівняти планувальники: FIFO, SJF, RR. Імітація в коді.",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(32),
            groupId="g1",
            teacherId="t8",
            classroomUrl="https://classroom.google.com/c/OS1/a/O1"
        ),
        HomeworkTask(
            id="hw10",
            subject="Комп'ютерна графіка",
            text="UV-розгортка і запікання нормалей. Підготувати коротке демо.",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(38),
            groupId="g1",
            teacherId="t9",
            classroomUrl="https://classroom.google.com/c/CG1/a/C1"
        ),
        HomeworkTask(
            id="hw11",
            subject="Філософія",
            text="Есе: «Технооптимізм vs техноскепсис». 800–1000 слів.",
            createdAt=datetime.now().isoformat(),
            dueDate=make_date(45),
            groupId="g1",
            teacherId="t10",
            classroomUrl="https://classroom.google.com/c/PHIL1/a/F1"
        )
    ]
    
    return StudentHomeworkResponse(
        tasks=tasks,
        totalWeeks=16  
    )


@router.get("/schedule/{student_id}", response_model=StudentSchedule)
async def fetch_student_schedule(student_id: str):
    return generate_mock_student_schedule(student_id)


@router.get("/homework/{student_id}", response_model=StudentHomeworkResponse)
async def fetch_student_homework(student_id: str):
    return generate_mock_homework(student_id)

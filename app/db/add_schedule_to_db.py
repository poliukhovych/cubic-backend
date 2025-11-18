#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для додавання розкладу в БД з хардкодженими даними.
Всі об'єкти визначені прямо в Python коді.
"""

import os
import uuid
from datetime import time
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from app.db.models import (
    Teacher, Room, Group, Course, Lesson, Timeslot, Schedule, Assignment,
    GroupCourse, TeacherCourse
)
from app.db.models.common_enums import TimeslotFrequency, CourseFrequency
from app.core.config import settings


def get_database_url() -> str:
    """Отримує DATABASE_URL з налаштувань або env змінної"""
    # Використовуємо settings.database_url, який читає з DATABASE_URL env var
    database_url = settings.database_url
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url


def create_sync_session() -> Session:
    """Створює синхронну сесію для роботи з БД"""
    database_url = get_database_url()
    # Конвертуємо async URL на sync URL якщо потрібно
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    elif database_url.startswith("postgresql://"):
        pass  # Вже правильний формат
    else:
        # Якщо інший формат, спробуємо як є
        pass
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def get_hardcoded_data():
    """
    Повертає всі хардкоджені дані для розкладу.
    Всі об'єкти визначені тут.
    """
    
    # ========== UUID для всіх об'єктів ==========
    # Викладачі
    teacher1_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
    teacher2_id = uuid.UUID('22222222-2222-2222-2222-222222222222')
    teacher3_id = uuid.UUID('33333333-3333-3333-3333-333333333333')
    
    # Аудиторії
    room1_id = uuid.UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
    room2_id = uuid.UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb')
    room3_id = uuid.UUID('cccccccc-cccc-cccc-cccc-cccccccccccc')
    
    # Групи
    group1_id = uuid.UUID('11111111-0000-0000-0000-000000000001')
    group2_id = uuid.UUID('11111111-0000-0000-0000-000000000002')
    group3_id = uuid.UUID('11111111-0000-0000-0000-000000000003')
    group4_id = uuid.UUID('11111111-0000-0000-0000-000000000004')
    
    # Курси
    course1_id = uuid.UUID('cccccccc-0000-0000-0000-000000000001')
    course2_id = uuid.UUID('cccccccc-0000-0000-0000-000000000002')
    course3_id = uuid.UUID('cccccccc-0000-0000-0000-000000000003')
    
    # Розклад
    schedule_id = uuid.UUID('ffffffff-ffff-ffff-ffff-ffffffffffff')
    
    # ========== ВИКЛАДАЧІ ==========
    teachers = [
        Teacher(
            teacher_id=teacher1_id,
            user_id=None,
            first_name="Іван",
            last_name="Петренко",
            patronymic="Олександрович",
            confirmed=True
        ),
        Teacher(
            teacher_id=teacher2_id,
            user_id=None,
            first_name="Марія",
            last_name="Коваленко",
            patronymic="Володимирівна",
            confirmed=True
        ),
        Teacher(
            teacher_id=teacher3_id,
            user_id=None,
            first_name="Олексій",
            last_name="Сидоренко",
            patronymic="Михайлович",
            confirmed=True
        ),
    ]
    
    # ========== АУДИТОРІЇ ==========
    rooms = [
        Room(
            room_id=room1_id,
            name="К-10",
            capacity=30
        ),
        Room(
            room_id=room2_id,
            name="К-11",
            capacity=25
        ),
        Room(
            room_id=room3_id,
            name="К-12",
            capacity=35
        ),
    ]
    
    # ========== ГРУПИ ==========
    groups = [
        Group(
            group_id=group1_id,
            name="ТТП-32",
            size=25,
            parent_group_id=None
        ),
        Group(
            group_id=group2_id,
            name="МІ-31",
            size=30,
            parent_group_id=None
        ),
        Group(
            group_id=group3_id,
            name="ІПЗ-31",
            size=28,
            parent_group_id=None
        ),
        Group(
            group_id=group4_id,
            name="ІПЗ-32",
            size=27,
            parent_group_id=None
        ),
    ]
    
    # ========== КУРСИ ==========
    courses = [
        Course(
            course_id=course1_id,
            name="Математичний аналіз",
            duration=60
        ),
        Course(
            course_id=course2_id,
            name="Програмування",
            duration=80
        ),
        Course(
            course_id=course3_id,
            name="Бази даних",
            duration=40
        ),
    ]
    
    # ========== ПАРИ (LESSONS) ==========
    lessons = [
        Lesson(
            lesson_id=1,
            start_time=time(8, 30),
            end_time=time(10, 5)
        ),
        Lesson(
            lesson_id=2,
            start_time=time(10, 25),
            end_time=time(12, 0)
        ),
        Lesson(
            lesson_id=3,
            start_time=time(12, 20),
            end_time=time(13, 55)
        ),
        Lesson(
            lesson_id=4,
            start_time=time(14, 15),
            end_time=time(15, 50)
        ),
    ]
    
    # ========== ЧАСОВІ СЛОТИ (TIMESLOTS) ==========
    # Створюємо timeslots для понеділка, середи, п'ятниці (дні 1, 3, 5)
    # для всіх пар (1-4) та всіх частот (all, odd, even)
    # timeslot_id буде автоматично згенерований (autoincrement)
    timeslots = []
    for day in [1, 3, 5]:  # Понеділок, Середа, П'ятниця
        for lesson_id in [1, 2, 3, 4]:
            for freq in [TimeslotFrequency.ALL, TimeslotFrequency.ODD, TimeslotFrequency.EVEN]:
                timeslots.append(
                    Timeslot(
                        day=day,
                        lesson_id=lesson_id,
                        frequency=freq
                    )
                )
    
    # ========== РОЗКЛАД ==========
    schedule = Schedule(
        schedule_id=schedule_id,
        label="ФКНК 2025-2026 семестр 1"
    )
    
    # ========== ПРИЗНАЧЕННЯ (ASSIGNMENTS) ==========
    # Приклад призначень для розкладу
    # timeslot_id буде отримано після додавання timeslots в БД
    # Тут зберігаємо інформацію про timeslot для пошуку
    assignments_data = [
        {
            'day': 1,  # Понеділок
            'lesson_id': 1,
            'frequency': TimeslotFrequency.ALL,
            'group_id': group1_id,
            'subgroup_no': 1,
            'course_id': course1_id,
            'teacher_id': teacher1_id,
            'room_id': room1_id,
            'course_type': 'lec'
        },
        {
            'day': 1,  # Понеділок
            'lesson_id': 2,
            'frequency': TimeslotFrequency.ALL,
            'group_id': group2_id,
            'subgroup_no': 1,
            'course_id': course2_id,
            'teacher_id': teacher2_id,
            'room_id': room2_id,
            'course_type': 'prac'
        },
        {
            'day': 3,  # Середа
            'lesson_id': 1,
            'frequency': TimeslotFrequency.ALL,
            'group_id': group3_id,
            'subgroup_no': 1,
            'course_id': course3_id,
            'teacher_id': teacher3_id,
            'room_id': room3_id,
            'course_type': 'lab'
        },
        {
            'day': 5,  # П'ятниця
            'lesson_id': 3,
            'frequency': TimeslotFrequency.ALL,
            'group_id': group4_id,
            'subgroup_no': 1,
            'course_id': course2_id,
            'teacher_id': teacher2_id,
            'room_id': room1_id,
            'course_type': 'prac'
        },
    ]
    
    # ========== GROUP_COURSE (зв'язки груп з курсами) ==========
    group_courses = [
        GroupCourse(
            group_id=group1_id,
            course_id=course1_id,
            count_per_week=2,
            frequency=CourseFrequency.WEEKLY
        ),
        GroupCourse(
            group_id=group2_id,
            course_id=course2_id,
            count_per_week=3,
            frequency=CourseFrequency.WEEKLY
        ),
        GroupCourse(
            group_id=group3_id,
            course_id=course3_id,
            count_per_week=2,
            frequency=CourseFrequency.WEEKLY
        ),
        GroupCourse(
            group_id=group4_id,
            course_id=course2_id,
            count_per_week=2,
            frequency=CourseFrequency.WEEKLY
        ),
    ]
    
    # ========== TEACHER_COURSE (зв'язки викладачів з курсами) ==========
    teacher_courses = [
        TeacherCourse(
            teacher_id=teacher1_id,
            course_id=course1_id
        ),
        TeacherCourse(
            teacher_id=teacher2_id,
            course_id=course2_id
        ),
        TeacherCourse(
            teacher_id=teacher3_id,
            course_id=course3_id
        ),
    ]
    
    return {
        'teachers': teachers,
        'rooms': rooms,
        'groups': groups,
        'courses': courses,
        'lessons': lessons,
        'timeslots': timeslots,
        'schedule': schedule,
        'assignments_data': assignments_data,  # Дані для assignments (без timeslot_id)
        'group_courses': group_courses,
        'teacher_courses': teacher_courses,
    }


def add_to_database_sync(session: Session, data: dict):
    """Синхронна функція для додавання всіх об'єктів в БД"""
    
    print("=== Додавання даних в БД ===\n")
    
    # Додаємо пари (lessons) - потрібні першими
    print(f"Додаю {len(data['lessons'])} пар...")
    for lesson in data['lessons']:
        session.merge(lesson)  # merge для уникнення дублікатів
    session.commit()
    print("✓ Пари додані\n")
    
    # Додаємо часові слоти (timeslots)
    print(f"Додаю {len(data['timeslots'])} часових слотів...")
    for timeslot in data['timeslots']:
        session.merge(timeslot)
    session.commit()
    print("✓ Часові слоти додані\n")
    
    # Додаємо викладачів
    print(f"Додаю {len(data['teachers'])} викладачів...")
    for teacher in data['teachers']:
        session.merge(teacher)
    session.commit()
    print("✓ Викладачі додані\n")
    
    # Додаємо аудиторії
    print(f"Додаю {len(data['rooms'])} аудиторій...")
    for room in data['rooms']:
        session.merge(room)
    session.commit()
    print("✓ Аудиторії додані\n")
    
    # Додаємо групи
    print(f"Додаю {len(data['groups'])} груп...")
    for group in data['groups']:
        session.merge(group)
    session.commit()
    print("✓ Групи додані\n")
    
    # Додаємо курси
    print(f"Додаю {len(data['courses'])} курсів...")
    for course in data['courses']:
        session.merge(course)
    session.commit()
    print("✓ Курси додані\n")
    
    # Додаємо розклад
    print("Додаю розклад...")
    session.merge(data['schedule'])
    session.commit()
    print("✓ Розклад додано\n")
    
    # Додаємо зв'язки GroupCourse
    print(f"Додаю {len(data['group_courses'])} зв'язків GroupCourse...")
    for gc in data['group_courses']:
        session.merge(gc)
    session.commit()
    print("✓ GroupCourse додані\n")
    
    # Додаємо зв'язки TeacherCourse
    print(f"Додаю {len(data['teacher_courses'])} зв'язків TeacherCourse...")
    for tc in data['teacher_courses']:
        session.merge(tc)
    session.commit()
    print("✓ TeacherCourse додані\n")
    
    # Додаємо призначення (assignments)
    # Спочатку знаходимо timeslot_id для кожного призначення
    print(f"Додаю {len(data['assignments_data'])} призначень...")
    for asg_data in data['assignments_data']:
        # Знаходимо timeslot по (day, lesson_id, frequency)
        timeslot = session.scalar(
            select(Timeslot).where(
                Timeslot.day == asg_data['day'],
                Timeslot.lesson_id == asg_data['lesson_id'],
                Timeslot.frequency == asg_data['frequency']
            )
        )
        if not timeslot:
            print(f"⚠ Помилка: не знайдено timeslot для day={asg_data['day']}, lesson={asg_data['lesson_id']}, freq={asg_data['frequency']}")
            continue
        
        assignment = Assignment(
            assignment_id=uuid.uuid4(),
            schedule_id=data['schedule'].schedule_id,
            timeslot_id=timeslot.timeslot_id,
            group_id=asg_data['group_id'],
            subgroup_no=asg_data['subgroup_no'],
            course_id=asg_data['course_id'],
            teacher_id=asg_data['teacher_id'],
            room_id=asg_data['room_id'],
            course_type=asg_data['course_type']
        )
        session.add(assignment)
    session.commit()
    print("✓ Призначення додані\n")
    
    print("=== Всі дані успішно додані в БД ===")


async def init_schedule_data():
    """
    Async функція для ініціалізації розкладу при старті backend.
    Викликається з lifespan контекст менеджера.
    """
    print("=== Ініціалізація розкладу ===\n")
    
    # Створюємо синхронну сесію
    session = create_sync_session()
    
    try:
        # Перевіряємо, чи дані вже існують (перевіряємо наявність розкладу)
        existing_schedule = session.scalar(
            select(Schedule).where(Schedule.schedule_id == uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"))
        )
        
        if existing_schedule:
            print("ℹ️  Дані розкладу вже існують, пропускаємо ініціалізацію\n")
            return
        
        # Отримуємо хардкоджені дані
        data = get_hardcoded_data()
        
        # Додаємо дані в БД
        add_to_database_sync(session, data)
    except Exception as e:
        print(f"\n❌ Помилка при ініціалізації розкладу: {e}")
        session.rollback()
        # Не піднімаємо помилку, щоб не зупинити старт backend
        print("⚠ Продовжуємо старт backend без ініціалізації розкладу\n")
    finally:
        session.close()


def main():
    """Головна функція для запуску скрипта окремо (якщо потрібно)"""
    import asyncio
    
    print("=== Скрипт додавання розкладу в БД ===\n")
    
    # Запускаємо async функцію
    asyncio.run(init_schedule_data())


if __name__ == "__main__":
    main()


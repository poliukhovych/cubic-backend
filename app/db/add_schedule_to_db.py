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
    User, UserRole,
    Teacher, Student, Admin, Room, Group, Course, Lesson, Timeslot, Schedule, Assignment,
    GroupCourse, TeacherCourse, StudentGroup, RegistrationRequest, RegistrationStatus
)
from app.db.models.common_enums import TimeslotFrequency, CourseFrequency, TeacherStatus, StudentStatus
from app.core.config import settings

# Флаг для відстеження, чи вже виконується ініціалізація
_initialization_in_progress = False
_initialization_completed = False


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
    # User для адміністратора (використовуємо user_id з токену)
    user_admin_id = uuid.UUID('4a9465b5-14ca-4b10-b6e0-20ca83eb6790')
    
    # Users для викладачів
    user_teacher1_id = uuid.UUID('00000000-0000-0000-0000-000000000011')
    user_teacher2_id = uuid.UUID('00000000-0000-0000-0000-000000000012')
    user_teacher3_id = uuid.UUID('00000000-0000-0000-0000-000000000013')
    
    # Users для студентів
    user_student1_id = uuid.UUID('00000000-0000-0000-0000-000000000021')
    user_student2_id = uuid.UUID('00000000-0000-0000-0000-000000000022')
    user_student3_id = uuid.UUID('00000000-0000-0000-0000-000000000023')
    
    # Адміністратор
    admin_id = uuid.UUID('99999999-9999-9999-9999-999999999999')
    
    # Викладачі
    teacher1_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
    teacher2_id = uuid.UUID('22222222-2222-2222-2222-222222222222')
    teacher3_id = uuid.UUID('33333333-3333-3333-3333-333333333333')
    
    # Студенти
    student1_id = uuid.UUID('20000000-0000-0000-0000-000000000001')
    student2_id = uuid.UUID('20000000-0000-0000-0000-000000000002')
    student3_id = uuid.UUID('20000000-0000-0000-0000-000000000003')
    
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
    
    # Заявки на реєстрацію
    registration1_id = uuid.UUID('aaaaaaaa-0000-0000-0000-000000000001')
    registration2_id = uuid.UUID('aaaaaaaa-0000-0000-0000-000000000002')
    registration3_id = uuid.UUID('aaaaaaaa-0000-0000-0000-000000000003')
    registration4_id = uuid.UUID('aaaaaaaa-0000-0000-0000-000000000004')
    registration5_id = uuid.UUID('aaaaaaaa-0000-0000-0000-000000000005')
    
    # ========== USERS (для адміністратора, викладачів та студентів) ==========
    users = [
        User(
            user_id=user_admin_id,
            google_sub="google_sub_admin_1",
            email="admin@example.com",
            first_name="Олександр",
            last_name="Адміністратор",
            patronymic="Петрович",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            user_id=user_teacher1_id,
            google_sub="google_sub_teacher_1",
            email="teacher1@university.edu",
            first_name="Іван",
            last_name="Петренко",
            patronymic="Олександрович",
            role=UserRole.TEACHER,
            is_active=True
        ),
        User(
            user_id=user_teacher2_id,
            google_sub="google_sub_teacher_2",
            email="teacher2@university.edu",
            first_name="Марія",
            last_name="Коваленко",
            patronymic="Володимирівна",
            role=UserRole.TEACHER,
            is_active=True
        ),
        User(
            user_id=user_teacher3_id,
            google_sub="google_sub_teacher_3",
            email="teacher3@university.edu",
            first_name="Олексій",
            last_name="Сидоренко",
            patronymic="Михайлович",
            role=UserRole.TEACHER,
            is_active=True
        ),
        User(
            user_id=user_student1_id,
            google_sub="google_sub_student_1",
            email="student1@university.edu",
            first_name="Дмитро",
            last_name="Іваненко",
            patronymic="Олегович",
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            user_id=user_student2_id,
            google_sub="google_sub_student_2",
            email="student2@university.edu",
            first_name="Анна",
            last_name="Шевченко",
            patronymic="Вікторівна",
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            user_id=user_student3_id,
            google_sub="google_sub_student_3",
            email="student3@university.edu",
            first_name="Олександр",
            last_name="Мельник",
            patronymic="Іванович",
            role=UserRole.STUDENT,
            is_active=True
        ),
    ]
    
    # ========== АДМІНІСТРАТОР ==========
    admin = Admin(
        admin_id=admin_id,
        user_id=user_admin_id,
        first_name="Олександр",
        last_name="Адміністратор",
        patronymic="Петрович"
    )
    
    # ========== ВИКЛАДАЧІ ==========
    teachers = [
        Teacher(
            teacher_id=teacher1_id,
            user_id=user_teacher1_id,
            first_name="Іван",
            last_name="Петренко",
            patronymic="Олександрович",
            status=TeacherStatus.ACTIVE
        ),
        Teacher(
            teacher_id=teacher2_id,
            user_id=user_teacher2_id,
            first_name="Марія",
            last_name="Коваленко",
            patronymic="Володимирівна",
            status=TeacherStatus.ACTIVE
        ),
        Teacher(
            teacher_id=teacher3_id,
            user_id=user_teacher3_id,
            first_name="Олексій",
            last_name="Сидоренко",
            patronymic="Михайлович",
            status=TeacherStatus.ACTIVE
        ),
    ]
    
    # ========== СТУДЕНТИ ==========
    students = [
        Student(
            student_id=student1_id,
            user_id=user_student1_id,
            group_id=group1_id,
            first_name="Дмитро",
            last_name="Іваненко",
            patronymic="Олегович",
            status=StudentStatus.ACTIVE
        ),
        Student(
            student_id=student2_id,
            user_id=user_student2_id,
            group_id=group2_id,
            first_name="Анна",
            last_name="Шевченко",
            patronymic="Вікторівна",
            status=StudentStatus.ACTIVE
        ),
        Student(
            student_id=student3_id,
            user_id=user_student3_id,
            group_id=group1_id,
            first_name="Олександр",
            last_name="Мельник",
            patronymic="Іванович",
            status=StudentStatus.ACTIVE
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
    # Максимум 4 пари на день (lesson_id 1-4) - обмеження в БД
    lessons = [
        Lesson(
            lesson_id=1,
            start_time=time(8, 40),
            end_time=time(10, 15)
        ),
        Lesson(
            lesson_id=2,
            start_time=time(10, 35),
            end_time=time(12, 10)
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
    # Створюємо timeslots для всіх робочих днів (понеділок-п'ятниця, дні 1-5)
    # для всіх пар (1-4) та всіх частот (all, odd, even)
    # timeslot_id буде автоматично згенерований (autoincrement)
    # Це дає: 5 днів * 4 пари * 3 частоти = 60 слотів загалом
    # Для frequency="all": 5 днів * 4 пари = 20 слотів
    timeslots = []
    for day in [1, 2, 3, 4, 5]:  # Понеділок - П'ятниця
        for lesson_id in [1, 2, 3, 4]:  # Максимум 4 пари на день
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
    
    # ========== STUDENT_GROUP (зв'язки студентів з групами) ==========
    # Ці зв'язки потрібні для SQL join у методі find_by_teacher_id
    # student1 (Іваненко) -> group1 (ТТП-32) -> course1 (Математичний аналіз) -> teacher1 (Петренко)
    # student2 (Шевченко) -> group2 (МІ-31) -> course2 (Програмування) -> teacher2 (Коваленко)
    # student3 (Мельник) -> group1 (ТТП-32) -> course1 (Математичний аналіз) -> teacher1 (Петренко)
    # group3 (ІПЗ-31) -> course3 (Бази даних) -> teacher3 (Сидоренко)
    # group4 (ІПЗ-32) -> course2 (Програмування) -> teacher2 (Коваленко)
    student_groups = [
        StudentGroup(
            student_id=student1_id,
            group_id=group1_id  # ТТП-32
        ),
        StudentGroup(
            student_id=student2_id,
            group_id=group2_id  # МІ-31
        ),
        StudentGroup(
            student_id=student3_id,
            group_id=group1_id  # ТТП-32
        ),
    ]
    
    # ========== ЗАЯВКИ НА РЕЄСТРАЦІЮ (REGISTRATION REQUESTS) ==========
    registration_requests = [
        # Заявка студента в очікуванні
        RegistrationRequest(
            request_id=registration1_id,
            google_sub="google_sub_registration_1",
            email="newstudent1@university.edu",
            first_name="Олег",
            last_name="Ткаченко",
            patronymic="Сергійович",
            requested_role=UserRole.STUDENT,
            status=RegistrationStatus.PENDING,
            group_id=group1_id,
            admin_note=None
        ),
        # Заявка викладача в очікуванні
        RegistrationRequest(
            request_id=registration2_id,
            google_sub="google_sub_registration_2",
            email="newteacher1@university.edu",
            first_name="Наталія",
            last_name="Бондаренко",
            patronymic="Ігорівна",
            requested_role=UserRole.TEACHER,
            status=RegistrationStatus.PENDING,
            group_id=None,
            admin_note=None
        ),
        # Заявка студента схвалена
        RegistrationRequest(
            request_id=registration3_id,
            google_sub="google_sub_registration_3",
            email="approvedstudent@university.edu",
            first_name="Віктор",
            last_name="Морозенко",
            patronymic="Андрійович",
            requested_role=UserRole.STUDENT,
            status=RegistrationStatus.APPROVED,
            group_id=group2_id,
            admin_note="Схвалено адміністратором"
        ),
        # Заявка викладача відхилена
        RegistrationRequest(
            request_id=registration4_id,
            google_sub="google_sub_registration_4",
            email="rejectedteacher@university.edu",
            first_name="Сергій",
            last_name="Лисенко",
            patronymic="Петрович",
            requested_role=UserRole.TEACHER,
            status=RegistrationStatus.REJECTED,
            group_id=None,
            admin_note="Недостатньо кваліфікації"
        ),
        # Заявка студента в очікуванні без групи
        RegistrationRequest(
            request_id=registration5_id,
            google_sub="google_sub_registration_5",
            email="newstudent2@university.edu",
            first_name="Катерина",
            last_name="Романенко",
            patronymic="Дмитрівна",
            requested_role=UserRole.STUDENT,
            status=RegistrationStatus.PENDING,
            group_id=None,
            admin_note=None
        ),
    ]
    
    return {
        'users': users,
        'admin': admin,
        'teachers': teachers,
        'students': students,
        'rooms': rooms,
        'groups': groups,
        'courses': courses,
        'lessons': lessons,
        'timeslots': timeslots,
        'schedule': schedule,
        'assignments_data': assignments_data,  # Дані для assignments (без timeslot_id)
        'group_courses': group_courses,
        'teacher_courses': teacher_courses,
        'student_groups': student_groups,
        'registration_requests': registration_requests,
    }


def add_to_database_sync(session: Session, data: dict):
    """Синхронна функція для додавання всіх об'єктів в БД"""
    
    print("=== Додавання даних в БД ===\n")
    
    # Додаємо users - потрібні першими для teachers
    print(f"Додаю {len(data['users'])} користувачів...")
    for user in data['users']:
        session.merge(user)  # merge для уникнення дублікатів
    session.commit()
    print("✓ Користувачі додані\n")
    
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
    
    # Додаємо адміністратора
    print("Додаю адміністратора...")
    session.merge(data['admin'])
    session.commit()
    print("✓ Адміністратор додано\n")
    
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
    
    # Додаємо заявки на реєстрацію (після groups, бо можуть мати group_id)
    print(f"Додаю {len(data['registration_requests'])} заявок на реєстрацію...")
    for registration in data['registration_requests']:
        session.merge(registration)
    session.commit()
    print("✓ Заявки на реєстрацію додані\n")
    
    # Додаємо студентів (після groups, бо students мають group_id)
    print(f"Додаю {len(data['students'])} студентів...")
    for student in data['students']:
        session.merge(student)
    session.commit()
    print("✓ Студенти додані\n")
    
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
    
    # Додаємо зв'язки StudentGroup (потрібні для SQL join)
    print(f"Додаю {len(data['student_groups'])} зв'язків StudentGroup...")
    for sg in data['student_groups']:
        session.merge(sg)
    session.commit()
    print("✓ StudentGroup додані\n")
    
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
    global _initialization_in_progress, _initialization_completed
    
    # Перевіряємо, чи вже виконується ініціалізація
    if _initialization_in_progress:
        return
    
    # Перевіряємо, чи вже завершена ініціалізація
    if _initialization_completed:
        return
    
    _initialization_in_progress = True
    
    try:
        print("=== Ініціалізація розкладу ===\n")
        
        # Створюємо синхронну сесію
        session = create_sync_session()
        
        try:
            # Перевіряємо, чи дані вже існують (перевіряємо наявність розкладу)
            existing_schedule = session.scalar(
                select(Schedule).where(Schedule.schedule_id == uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"))
            )
            
            # Отримуємо хардкоджені дані
            data = get_hardcoded_data()
            
            if existing_schedule:
                print("ℹ️  Розклад вже існує, перевіряю адміністратора та заявки...\n")
                
                # Перевіряємо та додаємо адміністратора
                existing_admin_user = session.scalar(
                    select(User).where(User.user_id == data['admin'].user_id)
                )
                if not existing_admin_user:
                    print("Додаю адміністратора...\n")
                    # Спочатку додаємо User
                    admin_user = next(u for u in data['users'] if u.user_id == data['admin'].user_id)
                    session.merge(admin_user)
                    session.commit()
                    # Потім додаємо Admin
                    session.merge(data['admin'])
                    session.commit()
                    print("✓ Адміністратор додано\n")
                else:
                    print("ℹ️  Адміністратор вже існує\n")
                
                # Завжди додаємо заявки через merge (не створить дублікатів, якщо вони вже є)
                print("Додаю заявки на реєстрацію (merge - не створить дублікатів)...\n")
                for registration in data['registration_requests']:
                    session.merge(registration)  # merge оновить існуючі або додасть нові
                session.commit()
                print(f"✓ {len(data['registration_requests'])} заявок на реєстрацію перевірено/додано\n")
                
                # Завжди додаємо зв'язки StudentGroup через merge (не створить дублікатів)
                print("Додаю зв'язки StudentGroup (merge - не створить дублікатів)...\n")
                for sg in data['student_groups']:
                    session.merge(sg)  # merge оновить існуючі або додасть нові
                session.commit()
                print(f"✓ {len(data['student_groups'])} зв'язків StudentGroup перевірено/додано\n")
                
                _initialization_completed = True
                return
            else:
                # Додаємо всі дані, включаючи заявки
                add_to_database_sync(session, data)
                _initialization_completed = True
        except Exception as e:
            print(f"\n❌ Помилка при ініціалізації розкладу: {e}")
            session.rollback()
            # Не піднімаємо помилку, щоб не зупинити старт backend
            print("⚠ Продовжуємо старт backend без ініціалізації розкладу\n")
        finally:
            session.close()
    finally:
        _initialization_in_progress = False


def main():
    """Головна функція для запуску скрипта окремо (якщо потрібно)"""
    import asyncio
    
    print("=== Скрипт додавання розкладу в БД ===\n")
    
    # Запускаємо async функцію
    asyncio.run(init_schedule_data())


if __name__ == "__main__":
    main()


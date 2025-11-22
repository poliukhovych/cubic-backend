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
from app.db.models.catalog.group import GroupType
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
    Розширені тестові дані для реалістичного розкладу.
    """
    
    # ========== БАЗОВІ UUID ==========
    # User для адміністратора (використовуємо user_id з токену)
    user_admin_id = uuid.UUID('4a9465b5-14ca-4b10-b6e0-20ca83eb6790')
    admin_id = uuid.UUID('99999999-9999-9999-9999-999999999999')
    schedule_id = uuid.UUID('ffffffff-ffff-ffff-ffff-ffffffffffff')
    
    # ========== КОНФІГУРАЦІЯ ДЛЯ ГЕНЕРАЦІЇ ДАНИХ ==========
    # Збільшено для отримання 40-50 призначень
    # 10 груп * 4-5 курсів = 40-50 призначень
    # У нас є 60 слотів загалом (20 "all" + 20 "odd" + 20 "even"), тому достатньо для 40-50 курсів
    NUM_TEACHERS = 15
    NUM_STUDENTS = 80
    NUM_GROUPS = 10
    NUM_COURSES = 50  # Збільшено для унікальних курсів для кожної групи
    NUM_ROOMS = 12
    NUM_REGISTRATIONS = 10
    
    # Списки для зберігання UUID
    user_teacher_ids = []
    teacher_ids = []
    user_student_ids = []
    student_ids = []
    group_ids = []
    course_ids = []
    room_ids = []
    registration_ids = []
    
    # Генерація UUID для всіх об'єктів
    for i in range(1, NUM_TEACHERS + 1):
        user_teacher_ids.append(uuid.UUID(f'00000000-0000-0000-0000-{i:012x}'))
        teacher_ids.append(uuid.UUID(f'11111111-1111-1111-1111-{i:012x}'))
    
    for i in range(1, NUM_STUDENTS + 1):
        user_student_ids.append(uuid.UUID(f'00000000-0000-0000-0000-{200 + i:012x}'))
        student_ids.append(uuid.UUID(f'20000000-0000-0000-0000-{i:012x}'))
    
    for i in range(1, NUM_GROUPS + 1):
        group_ids.append(uuid.UUID(f'11111111-0000-0000-0000-{i:012x}'))
    
    for i in range(1, NUM_COURSES + 1):
        course_ids.append(uuid.UUID(f'cccccccc-0000-0000-0000-{i:012x}'))
    
    for i in range(1, NUM_ROOMS + 1):
        room_ids.append(uuid.UUID(f'aaaaaaaa-aaaa-aaaa-aaaa-{i:012x}'))
    
    for i in range(1, NUM_REGISTRATIONS + 1):
        registration_ids.append(uuid.UUID(f'aaaaaaaa-0000-0000-0000-{i:012x}'))
    
    # ========== USERS (для адміністратора, викладачів та студентів) ==========
    # Списки українських імен для генерації
    teacher_first_names = ["Іван", "Марія", "Олексій", "Наталія", "Андрій", "Олена", "Сергій", 
                          "Тетяна", "Володимир", "Юлія", "Дмитро", "Катерина", "Олександр", "Анна", "Михайло"]
    teacher_last_names = ["Петренко", "Коваленко", "Сидоренко", "Бондаренко", "Мельник", "Шевченко",
                         "Ткаченко", "Морозенко", "Лисенко", "Романенко", "Іваненко", "Савченко",
                         "Кравченко", "Олійник", "Гончаренко"]
    teacher_patronymics_male = ["Олександрович", "Володимирович", "Михайлович", "Сергійович", "Андрійович",
                               "Дмитрович", "Іванович", "Олегович", "Петрович", "Вікторович"]
    teacher_patronymics_female = ["Олександрівна", "Володимирівна", "Михайлівна", "Сергіївна", "Андріївна",
                                 "Дмитрівна", "Іванівна", "Олегівна", "Петрівна", "Вікторівна"]
    
    student_first_names = ["Дмитро", "Анна", "Олександр", "Марія", "Андрій", "Олена", "Сергій", "Тетяна",
                          "Володимир", "Юлія", "Іван", "Катерина", "Михайло", "Наталія", "Олексій", "Вікторія",
                          "Роман", "Оксана", "Василь", "Ірина", "Павло", "Світлана", "Богдан", "Людмила",
                          "Максим", "Ольга", "Віталій", "Галина", "Юрій", "Надія", "Ігор", "Лариса",
                          "Олег", "Тетяна", "Руслан", "Валентина", "Тарас", "Любов", "Станіслав", "Ніна"]
    student_last_names = ["Іваненко", "Шевченко", "Мельник", "Петренко", "Коваленко", "Сидоренко",
                         "Ткаченко", "Морозенко", "Лисенко", "Романенко", "Бондаренко", "Савченко",
                         "Кравченко", "Олійник", "Гончаренко", "Бондар", "Коваль", "Шевчук", "Мельничук",
                         "Ткачук", "Мороз", "Лисенко", "Романюк", "Іванюк", "Петрук", "Ковальчук"]
    student_patronymics = ["Олегович", "Вікторівна", "Іванович", "Олександрович", "Дмитрович", "Сергійович",
                          "Андрійович", "Володимирович", "Михайлович", "Петрович", "Олегівна", "Вікторівна",
                          "Іванівна", "Олександрівна", "Дмитрівна", "Сергіївна", "Андріївна", "Володимирівна",
                          "Михайлівна", "Петрівна"]
    
    users = []
    
    # Адміністратор
    users.append(User(
        user_id=user_admin_id,
        google_sub="google_sub_admin_1",
        email="admin@example.com",
        first_name="Олександр",
        last_name="Адміністратор",
        patronymic="Петрович",
        role=UserRole.ADMIN,
        is_active=True
    ))
    
    # Викладачі
    for i in range(NUM_TEACHERS):
        first_name = teacher_first_names[i % len(teacher_first_names)]
        last_name = teacher_last_names[i % len(teacher_last_names)]
        # Визначаємо стать за ім'ям (спрощено)
        is_female = first_name in ["Марія", "Наталія", "Олена", "Тетяна", "Юлія", "Катерина", "Анна"]
        patronymic = teacher_patronymics_female[i % len(teacher_patronymics_female)] if is_female else teacher_patronymics_male[i % len(teacher_patronymics_male)]
        
        users.append(User(
            user_id=user_teacher_ids[i],
            google_sub=f"google_sub_teacher_{i+1}",
            email=f"teacher{i+1}@university.edu",
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            role=UserRole.TEACHER,
            is_active=True
        ))
    
    # Студенти
    for i in range(NUM_STUDENTS):
        first_name = student_first_names[i % len(student_first_names)]
        last_name = student_last_names[i % len(student_last_names)]
        patronymic = student_patronymics[i % len(student_patronymics)]
        
        users.append(User(
            user_id=user_student_ids[i],
            google_sub=f"google_sub_student_{i+1}",
            email=f"student{i+1}@university.edu",
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            role=UserRole.STUDENT,
            is_active=True
        ))
    
    # ========== АДМІНІСТРАТОР ==========
    admin = Admin(
        admin_id=admin_id,
        user_id=user_admin_id,
        first_name="Олександр",
        last_name="Адміністратор",
        patronymic="Петрович"
    )
    
    # ========== ВИКЛАДАЧІ ==========
    teachers = []
    for i in range(NUM_TEACHERS):
        user = users[1 + i]  # Перший user - адмін, потім викладачі
        teachers.append(Teacher(
            teacher_id=teacher_ids[i],
            user_id=user_teacher_ids[i],
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            status=TeacherStatus.ACTIVE
        ))
    
    # ========== СТУДЕНТИ ==========
    # Розподіляємо студентів по групах (приблизно рівномірно)
    students = []
    students_per_group = NUM_STUDENTS // NUM_GROUPS
    for i in range(NUM_STUDENTS):
        user = users[1 + NUM_TEACHERS + i]  # Після адміна та викладачів
        group_index = i // students_per_group if students_per_group > 0 else i % NUM_GROUPS
        if group_index >= NUM_GROUPS:
            group_index = NUM_GROUPS - 1
        
        students.append(Student(
            student_id=student_ids[i],
            user_id=user_student_ids[i],
            group_id=group_ids[group_index],
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            status=StudentStatus.ACTIVE
        ))
    
    # ========== АУДИТОРІЇ ==========
    # Аудиторії повинні мати достатню місткість для груп
    # ВАЖЛИВО: Якщо курс має кілька груп, сумарний розмір ВСІХ груп має поміщатися в аудиторію!
    # Тому потрібні великі аудиторії (60-100), щоб вмістити кілька груп одночасно
    rooms = []
    room_names = ["К-10", "К-11", "К-12", "К-13", "К-14", "К-15", "К-16", "К-17", "К-18", "К-19", "К-20", "К-21"]
    # Місткість має бути достатньою для кількох груп одночасно (наприклад, 2 групи по 30 = 60)
    room_capacities = [60, 70, 80, 60, 70, 80, 60, 70, 80, 60, 70, 80]
    
    for i in range(NUM_ROOMS):
        rooms.append(Room(
            room_id=room_ids[i],
            name=room_names[i % len(room_names)],
            capacity=room_capacities[i % len(room_capacities)]
        ))
    
    # ========== ГРУПИ ==========
    groups = []
    group_prefixes = ["ТТП", "МІ", "ІПЗ", "КН", "ПМ", "ФІ", "ЕК", "МТ", "СА", "КІ"]
    group_courses_list = [1, 2, 3, 4, 1, 2, 3, 4, 1, 2]  # Курси навчання (1-4)
    group_types = [GroupType.BACHELOR] * 8 + [GroupType.MASTER] * 2  # Більшість бакалаврів
    group_sizes = [25, 30, 28, 27, 26, 29, 24, 31, 25, 28]  # Розміри груп (мають поміщатися в аудиторії)
    
    for i in range(NUM_GROUPS):
        prefix = group_prefixes[i % len(group_prefixes)]
        course_num = group_courses_list[i % len(group_courses_list)]
        group_num = (i % 3) + 1  # 1, 2, або 3
        name = f"{prefix}-{course_num}{group_num}"
        
        groups.append(Group(
            group_id=group_ids[i],
            name=name,
            size=group_sizes[i % len(group_sizes)],
            type=group_types[i % len(group_types)],
            course=group_courses_list[i % len(group_courses_list)],
            parent_group_id=None
        ))
    
    # ========== КУРСИ ==========
    courses = []
    course_names = [
        "Математичний аналіз", "Програмування", "Бази даних", "Дискретна математика",
        "Алгоритми та структури даних", "Операційні системи", "Комп'ютерні мережі",
        "Веб-програмування", "Машинне навчання", "Комп'ютерна графіка",
        "Теорія ймовірностей", "Лінійна алгебра", "Архітектура комп'ютерів",
        "Програмна інженерія", "Кібербезпека", "Штучний інтелект",
        "Мобільні додатки", "Хмарні обчислення", "Великі дані", "Розподілені системи",
        "Обчислювальна геометрія", "Теорія алгоритмів", "Компілятори", "Паралельні обчислення",
        "Комп'ютерна безпека", "Криптографія", "Блокчейн технології", "Інтернет речей",
        "Розробка програмного забезпечення", "Тестування програмного забезпечення", "Проектний менеджмент",
        "Економіка програмної інженерії", "Етика в IT", "Історія обчислювальної техніки",
        "Квантові обчислення", "Біоінформатика", "Комп'ютерна лінгвістика", "Штучна нейронна мережа",
        "Глибоке навчання", "Обробка природної мови", "Комп'ютерний зір", "Робототехніка",
        "Системний аналіз", "Управління проектами", "Аналіз даних", "Статистика",
        "Математична логіка", "Теорія множин", "Теорія графів", "Комбінаторика"
    ]
    course_durations = [60, 80, 40, 60, 80, 60, 40, 80, 60, 40, 60, 60, 40, 80, 60, 60, 80, 60, 40, 60,
                       60, 80, 40, 60, 80, 60, 40, 80, 60, 40, 60, 60, 40, 80, 60, 60, 80, 60, 40, 60,
                       60, 80, 40, 60, 80, 60, 40, 80, 60, 40]
    
    for i in range(NUM_COURSES):
        courses.append(Course(
            course_id=course_ids[i],
            name=course_names[i % len(course_names)],
            code=f"CS{i+1:03d}",
            duration=course_durations[i % len(course_durations)]
        ))
    
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
    # Не створюємо призначення заздалегідь - мікросервіс сам їх створить
    # Це тільки для тестових даних, якщо потрібно
    assignments_data = []
    
    # ========== GROUP_COURSE (зв'язки груп з курсами) ==========
    # Кожна група має 4-5 курсів, всі з countPerWeek=1
    # ВАЖЛИВО: Кожна група має УНІКАЛЬНІ курси, щоб уникнути об'єднання груп в один курс
    # Це гарантує, що кожен курс має тільки одну групу, і сумарний розмір = розмір групи
    # 10 груп * 4-5 курсів = 40-50 курсів, кожен з countPerWeek=1 = 40-50 призначень
    # Використовуємо різні частоти (WEEKLY, ODD, EVEN) для використання всіх доступних слотів
    group_courses = []
    course_counter = 0  # Лічильник для унікальних курсів
    for group_idx in range(NUM_GROUPS):
        num_courses = 4 + (group_idx % 2)  # 4 або 5 курсів на групу (для отримання 40-50 загалом)
        
        for course_idx in range(num_courses):
            # Кожна група має унікальні курси (не повторюються між групами)
            # Це гарантує, що курси не об'єднуються між групами
            course_id = course_ids[course_counter % NUM_COURSES]
            course_counter += 1
            
            # Всі курси 1 раз на тиждень
            count_per_week = 1
            
            # Використовуємо різні частоти для розподілу по всіх доступних слотах
            # Більшість курсів WEEKLY (використовують слоти "all")
            # Деякі курси ODD/EVEN (використовують додаткові слоти)
            if course_idx % 4 == 0:
                frequency = CourseFrequency.ODD
            elif course_idx % 5 == 0:
                frequency = CourseFrequency.EVEN
            else:
                frequency = CourseFrequency.WEEKLY
            
            group_courses.append(GroupCourse(
                group_id=group_ids[group_idx],
                course_id=course_id,
                count_per_week=count_per_week,
                frequency=frequency
            ))
    
    # ========== TEACHER_COURSE (зв'язки викладачів з курсами) ==========
    # Переконаємося, що кожен курс має рівно одного викладача
    # Використаємо унікальні курси з GroupCourse, щоб призначити викладачів
    teacher_courses = []
    
    # Зберігаємо які курси використовуються в GroupCourse
    used_courses = set()
    for gc in group_courses:
        used_courses.add(gc.course_id)
    
    # Призначимо викладачів на всі курси, які використовуються
    # Кожен курс має рівно одного викладача
    course_to_teacher = {}
    teacher_course_count = {}  # Підрахунок курсів на викладача
    
    for course_id in used_courses:
        # Знайдемо викладача з найменшою кількістю курсів
        teacher_idx = min(range(NUM_TEACHERS), 
                         key=lambda i: teacher_course_count.get(teacher_ids[i], 0))
        
        course_to_teacher[course_id] = teacher_ids[teacher_idx]
        teacher_course_count[teacher_ids[teacher_idx]] = teacher_course_count.get(teacher_ids[teacher_idx], 0) + 1
        
        teacher_courses.append(TeacherCourse(
            teacher_id=teacher_ids[teacher_idx],
            course_id=course_id
        ))
    
    # ========== STUDENT_GROUP (зв'язки студентів з групами) ==========
    # Ці зв'язки потрібні для SQL join у методі find_by_teacher_id
    # Студенти вже мають group_id в Student, але потрібні зв'язки для join
    student_groups = []
    students_per_group = NUM_STUDENTS // NUM_GROUPS
    for student_idx in range(NUM_STUDENTS):
        group_idx = student_idx // students_per_group if students_per_group > 0 else student_idx % NUM_GROUPS
        if group_idx >= NUM_GROUPS:
            group_idx = NUM_GROUPS - 1
        
        student_groups.append(StudentGroup(
            student_id=student_ids[student_idx],
            group_id=group_ids[group_idx]
        ))
    
    # ========== ЗАЯВКИ НА РЕЄСТРАЦІЮ (REGISTRATION REQUESTS) ==========
    registration_requests = []
    reg_first_names = ["Олег", "Наталія", "Віктор", "Сергій", "Катерина", "Андрій", "Олена", "Дмитро", "Ірина", "Павло"]
    reg_last_names = ["Ткаченко", "Бондаренко", "Морозенко", "Лисенко", "Романенко", "Коваль", "Шевчук", "Мельник", "Петренко", "Сидоренко"]
    reg_patronymics = ["Сергійович", "Ігорівна", "Андрійович", "Петрович", "Дмитрівна", "Олександрович", "Володимирівна", "Михайлович", "Олегович", "Вікторівна"]
    reg_statuses = [RegistrationStatus.PENDING, RegistrationStatus.PENDING, RegistrationStatus.APPROVED, 
                   RegistrationStatus.REJECTED, RegistrationStatus.PENDING, RegistrationStatus.PENDING,
                   RegistrationStatus.APPROVED, RegistrationStatus.PENDING, RegistrationStatus.REJECTED, RegistrationStatus.PENDING]
    reg_roles = [UserRole.STUDENT, UserRole.TEACHER, UserRole.STUDENT, UserRole.TEACHER, UserRole.STUDENT,
                UserRole.STUDENT, UserRole.TEACHER, UserRole.STUDENT, UserRole.TEACHER, UserRole.STUDENT]
    reg_notes = [None, None, "Схвалено адміністратором", "Недостатньо кваліфікації", None, None,
                "Схвалено", None, "Не відповідає вимогам", None]
    
    for i in range(NUM_REGISTRATIONS):
        # Визначаємо чи студент чи викладач
        is_student = reg_roles[i] == UserRole.STUDENT
        group_id = None
        if is_student and reg_statuses[i] == RegistrationStatus.APPROVED:
            # Схвалені студенти отримують групу
            group_id = group_ids[i % NUM_GROUPS]
        elif is_student and i % 3 == 0:
            # Деякі студенти в очікуванні вже мають групу
            group_id = group_ids[i % NUM_GROUPS]
        
        registration_requests.append(RegistrationRequest(
            request_id=registration_ids[i],
            google_sub=f"google_sub_registration_{i+1}",
            email=f"new{'student' if is_student else 'teacher'}{i+1}@university.edu",
            first_name=reg_first_names[i % len(reg_first_names)],
            last_name=reg_last_names[i % len(reg_last_names)],
            patronymic=reg_patronymics[i % len(reg_patronymics)],
            requested_role=reg_roles[i],
            status=reg_statuses[i],
            group_id=group_id,
            admin_note=reg_notes[i]
        ))
    
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


"""
Модуль для ініціалізації тестових даних в БД.
Заповнює всю БД тестовими даними, якщо їх немає.
"""
import uuid
from datetime import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker
from app.db.models import (
    User, UserRole,
    Teacher, Student, Admin,
    Course, Group, Room, Lesson,
    Timeslot, Schedule, Assignment,
    GroupCourse, TeacherCourse, StudentGroup,
    RegistrationRequest, RegistrationStatus
)
from app.db.models.common_enums import (
    TimeslotFrequency, CourseFrequency,
    StudentStatus, TeacherStatus
)


async def _check_column_exists(session: AsyncSession, table_name: str, column_name: str) -> bool:
    """Перевіряє, чи існує стовпець в таблиці"""
    from sqlalchemy import text as sql_text
    try:
        result = await session.execute(
            sql_text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=:table_name AND column_name=:column_name
            """),
            {"table_name": table_name, "column_name": column_name}
        )
        return result.scalar() is not None
    except Exception:
        return False


async def _check_table_exists(session: AsyncSession, table_name: str) -> bool:
    """Перевіряє, чи існує таблиця в БД"""
    from sqlalchemy import text as sql_text
    try:
        result = await session.execute(
            sql_text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                )
            """),
            {"table_name": table_name}
        )
        return result.scalar() is True
    except Exception:
        return False


async def init_test_data():
    """
    Ініціалізує всю БД тестовими даними, якщо їх немає.
    Перевіряє наявність даних перед заповненням.
    """
    async with async_session_maker() as session:
        try:
            # Спочатку перевіряємо, чи існує таблиця users
            # Якщо таблиця не існує, це означає, що міграції ще не виконані
            if not await _check_table_exists(session, "users"):
                print("ℹ️  Таблиці ще не створені (міграції не виконані), пропускаємо ініціалізацію тестових даних")
                return

            # Перевіряємо, чи є дані в БД
            try:
                result = await session.execute(select(User).limit(1))
                if result.scalar_one_or_none() is not None:
                    print("ℹ️  Тестові дані вже існують, пропускаємо ініціалізацію")
                    return
            except Exception as e:
                # Якщо помилка при запиті (наприклад, таблиця ще не готова), пропускаємо ініціалізацію
                print(f"ℹ️  Не вдалося перевірити наявність даних: {e}")
                print("ℹ️  Пропускаємо ініціалізацію тестових даних")
                return

            print("=== Ініціалізація тестових даних ===\n")

            # Створюємо всі дані в правильному порядку (з урахуванням foreign keys)
            await _create_users(session)
            await _create_lessons(session)
            await _create_groups(session)
            await _create_courses(session)
            await _create_rooms(session)
            await _create_teachers(session)
            await _create_students(session)
            await _create_admins(session)
            await _create_timeslots(session)
            await _create_schedules(session)
            await _create_group_courses(session)
            await _create_teacher_courses(session)
            await _create_student_groups(session)
            await _create_assignments(session)
            await _create_registration_requests(session)

            await session.commit()
            print("\n=== Тестові дані успішно ініціалізовано ===\n")

        except Exception as e:
            try:
                await session.rollback()
            except Exception:
                pass  # Ігноруємо помилки при rollback
            print(f"⚠️  Помилка при ініціалізації тестових даних: {e}")
            import traceback
            print(traceback.format_exc())
            # Не піднімаємо помилку, щоб не зупинити старт додатку
            # raise


# UUID константи для тестових даних
USER_ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_TEACHER1_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
USER_TEACHER2_ID = uuid.UUID("00000000-0000-0000-0000-000000000012")
USER_TEACHER3_ID = uuid.UUID("00000000-0000-0000-0000-000000000013")
USER_STUDENT1_ID = uuid.UUID("00000000-0000-0000-0000-000000000021")
USER_STUDENT2_ID = uuid.UUID("00000000-0000-0000-0000-000000000022")
USER_STUDENT3_ID = uuid.UUID("00000000-0000-0000-0000-000000000023")

TEACHER1_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TEACHER2_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
TEACHER3_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")

STUDENT1_ID = uuid.UUID("20000000-0000-0000-0000-000000000001")
STUDENT2_ID = uuid.UUID("20000000-0000-0000-0000-000000000002")
STUDENT3_ID = uuid.UUID("20000000-0000-0000-0000-000000000003")

ADMIN1_ID = uuid.UUID("30000000-0000-0000-0000-000000000001")

COURSE1_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000001")
COURSE2_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000002")
COURSE3_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000003")
COURSE4_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000004")

ROOM1_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
ROOM2_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
ROOM3_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
ROOM4_ID = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")

GROUP1_ID = uuid.UUID("11111111-0000-0000-0000-000000000001")
GROUP2_ID = uuid.UUID("11111111-0000-0000-0000-000000000002")
GROUP3_ID = uuid.UUID("11111111-0000-0000-0000-000000000003")
GROUP4_ID = uuid.UUID("11111111-0000-0000-0000-000000000004")

SCHEDULE1_ID = uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")


async def _create_users(session: AsyncSession):
    """Створює тестових користувачів"""
    users = [
        User(
            user_id=USER_ADMIN_ID,
            google_sub="google_sub_admin_1",
            email="admin@university.edu",
            first_name="Олександр",
            last_name="Адміністратор",
            patronymic="Петрович",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            user_id=USER_TEACHER1_ID,
            google_sub="google_sub_teacher_1",
            email="teacher1@university.edu",
            first_name="Іван",
            last_name="Петренко",
            patronymic="Олександрович",
            role=UserRole.TEACHER,
            is_active=True
        ),
        User(
            user_id=USER_TEACHER2_ID,
            google_sub="google_sub_teacher_2",
            email="teacher2@university.edu",
            first_name="Марія",
            last_name="Коваленко",
            patronymic="Володимирівна",
            role=UserRole.TEACHER,
            is_active=True
        ),
        User(
            user_id=USER_TEACHER3_ID,
            google_sub="google_sub_teacher_3",
            email="teacher3@university.edu",
            first_name="Олексій",
            last_name="Сидоренко",
            patronymic="Михайлович",
            role=UserRole.TEACHER,
            is_active=True
        ),
        User(
            user_id=USER_STUDENT1_ID,
            google_sub="google_sub_student_1",
            email="student1@university.edu",
            first_name="Дмитро",
            last_name="Іваненко",
            patronymic="Олегович",
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            user_id=USER_STUDENT2_ID,
            google_sub="google_sub_student_2",
            email="student2@university.edu",
            first_name="Анна",
            last_name="Шевченко",
            patronymic="Вікторівна",
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            user_id=USER_STUDENT3_ID,
            google_sub="google_sub_student_3",
            email="student3@university.edu",
            first_name="Олександр",
            last_name="Мельник",
            patronymic="Іванович",
            role=UserRole.STUDENT,
            is_active=True
        ),
    ]
    for user in users:
        session.add(user)
    print("✓ Користувачі створені")


async def _create_teachers(session: AsyncSession):
    """Створює тестових викладачів"""
    teachers = [
        Teacher(
            teacher_id=TEACHER1_ID,
            user_id=USER_TEACHER1_ID,
            first_name="Іван",
            last_name="Петренко",
            patronymic="Олександрович",
            status=TeacherStatus.ACTIVE
        ),
        Teacher(
            teacher_id=TEACHER2_ID,
            user_id=USER_TEACHER2_ID,
            first_name="Марія",
            last_name="Коваленко",
            patronymic="Володимирівна",
            status=TeacherStatus.ACTIVE
        ),
        Teacher(
            teacher_id=TEACHER3_ID,
            user_id=USER_TEACHER3_ID,
            first_name="Олексій",
            last_name="Сидоренко",
            patronymic="Михайлович",
            status=TeacherStatus.ACTIVE
        ),
    ]
    for teacher in teachers:
        session.add(teacher)
    print("✓ Викладачі створені")


async def _create_students(session: AsyncSession):
    """Створює тестових студентів"""
    students = [
        Student(
            student_id=STUDENT1_ID,
            user_id=USER_STUDENT1_ID,
            group_id=GROUP1_ID,
            first_name="Дмитро",
            last_name="Іваненко",
            patronymic="Олегович",
            status=StudentStatus.ACTIVE
        ),
        Student(
            student_id=STUDENT2_ID,
            user_id=USER_STUDENT2_ID,
            group_id=GROUP2_ID,
            first_name="Анна",
            last_name="Шевченко",
            patronymic="Вікторівна",
            status=StudentStatus.ACTIVE
        ),
        Student(
            student_id=STUDENT3_ID,
            user_id=USER_STUDENT3_ID,
            group_id=GROUP1_ID,
            first_name="Олександр",
            last_name="Мельник",
            patronymic="Іванович",
            status=StudentStatus.ACTIVE
        ),
    ]
    for student in students:
        session.add(student)
    print("✓ Студенти створені")


async def _create_admins(session: AsyncSession):
    """Створює тестових адміністраторів"""
    admins = [
        Admin(
            admin_id=ADMIN1_ID,
            user_id=USER_ADMIN_ID,
            first_name="Олександр",
            last_name="Адміністратор",
            patronymic="Петрович"
        ),
    ]
    for admin in admins:
        session.add(admin)
    print("✓ Адміністратори створені")


async def _create_courses(session: AsyncSession):
    """Створює тестові курси"""
    courses_data = [
        {"course_id": COURSE1_ID, "name": "Математичний аналіз", "duration": 60},
        {"course_id": COURSE2_ID, "name": "Програмування", "duration": 80},
        {"course_id": COURSE3_ID, "name": "Бази даних", "duration": 40},
        {"course_id": COURSE4_ID, "name": "Алгоритми та структури даних", "duration": 60},
    ]
    
    for data in courses_data:
        course = Course(
            course_id=data["course_id"],
            name=data["name"],
            duration=data["duration"]
        )
        session.add(course)
    
    print("✓ Курси створені")


async def _create_rooms(session: AsyncSession):
    """Створює тестові аудиторії"""
    rooms = [
        Room(
            room_id=ROOM1_ID,
            name="К-10",
            capacity=30
        ),
        Room(
            room_id=ROOM2_ID,
            name="К-11",
            capacity=25
        ),
        Room(
            room_id=ROOM3_ID,
            name="К-12",
            capacity=35
        ),
        Room(
            room_id=ROOM4_ID,
            name="К-20",
            capacity=40
        ),
    ]
    for room in rooms:
        session.add(room)
    print("✓ Аудиторії створені")


async def _create_groups(session: AsyncSession):
    """Створює тестові групи"""
    groups_data = [
        {"group_id": GROUP1_ID, "name": "ТТП-32", "size": 25},
        {"group_id": GROUP2_ID, "name": "МІ-31", "size": 30},
        {"group_id": GROUP3_ID, "name": "ІПЗ-31", "size": 28},
        {"group_id": GROUP4_ID, "name": "ІПЗ-32", "size": 27},
    ]
    
    for data in groups_data:
        group = Group(
            group_id=data["group_id"],
            name=data["name"],
            size=data["size"],
            parent_group_id=None
        )
        session.add(group)
    
    print("✓ Групи створені")


async def _create_lessons(session: AsyncSession):
    """Створює тестові пари (lessons)"""
    # Максимум 4 пари на день (lesson_id 1-4) - обмеження в БД (ck_lessons_id_range)
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
    for lesson in lessons:
        session.add(lesson)
    print("✓ Пари створені")


async def _create_timeslots(session: AsyncSession):
    """Створює тестові часові слоти"""
    # Створюємо timeslots для всіх робочих днів (понеділок-п'ятниця, дні 1-5)
    # для всіх пар (1-4) та всіх частот (all, odd, even)
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
    for timeslot in timeslots:
        session.add(timeslot)
    print("✓ Часові слоти створені")


async def _create_schedules(session: AsyncSession):
    """Створює тестові розклади"""
    schedules = [
        Schedule(
            schedule_id=SCHEDULE1_ID,
            label="ФКНК 2025-2026 семестр 1"
        ),
    ]
    for schedule in schedules:
        session.add(schedule)
    print("✓ Розклади створені")


async def _create_group_courses(session: AsyncSession):
    """Створює зв'язки груп з курсами"""
    group_courses = [
        GroupCourse(
            group_id=GROUP1_ID,
            course_id=COURSE1_ID,
            count_per_week=2,
            frequency=CourseFrequency.WEEKLY
        ),
        GroupCourse(
            group_id=GROUP1_ID,
            course_id=COURSE2_ID,
            count_per_week=3,
            frequency=CourseFrequency.WEEKLY
        ),
        GroupCourse(
            group_id=GROUP2_ID,
            course_id=COURSE2_ID,
            count_per_week=3,
            frequency=CourseFrequency.WEEKLY
        ),
        GroupCourse(
            group_id=GROUP2_ID,
            course_id=COURSE4_ID,
            count_per_week=2,
            frequency=CourseFrequency.WEEKLY
        ),
        GroupCourse(
            group_id=GROUP3_ID,
            course_id=COURSE3_ID,
            count_per_week=2,
            frequency=CourseFrequency.WEEKLY
        ),
        GroupCourse(
            group_id=GROUP4_ID,
            course_id=COURSE2_ID,
            count_per_week=2,
            frequency=CourseFrequency.WEEKLY
        ),
    ]
    for gc in group_courses:
        session.add(gc)
    print("✓ Зв'язки груп з курсами створені")


async def _create_teacher_courses(session: AsyncSession):
    """Створює зв'язки викладачів з курсами"""
    teacher_courses = [
        TeacherCourse(
            teacher_id=TEACHER1_ID,
            course_id=COURSE1_ID
        ),
        TeacherCourse(
            teacher_id=TEACHER2_ID,
            course_id=COURSE2_ID
        ),
        TeacherCourse(
            teacher_id=TEACHER3_ID,
            course_id=COURSE3_ID
        ),
        TeacherCourse(
            teacher_id=TEACHER2_ID,
            course_id=COURSE4_ID
        ),
    ]
    for tc in teacher_courses:
        session.add(tc)
    print("✓ Зв'язки викладачів з курсами створені")


async def _create_student_groups(session: AsyncSession):
    """Створює зв'язки студентів з групами"""
    student_groups = [
        StudentGroup(
            student_id=STUDENT1_ID,
            group_id=GROUP1_ID
        ),
        StudentGroup(
            student_id=STUDENT2_ID,
            group_id=GROUP2_ID
        ),
        StudentGroup(
            student_id=STUDENT3_ID,
            group_id=GROUP1_ID
        ),
    ]
    for sg in student_groups:
        session.add(sg)
    print("✓ Зв'язки студентів з групами створені")


async def _create_assignments(session: AsyncSession):
    """Створює тестові призначення (assignments)"""
    assignments_data = [
        {
            'day': 1,
            'lesson_id': 1,
            'frequency': TimeslotFrequency.ALL,
            'group_id': GROUP1_ID,
            'subgroup_no': 1,
            'course_id': COURSE1_ID,
            'teacher_id': TEACHER1_ID,
            'room_id': ROOM1_ID,
            'course_type': 'lec'
        },
        {
            'day': 1,
            'lesson_id': 2,
            'frequency': TimeslotFrequency.ALL,
            'group_id': GROUP2_ID,
            'subgroup_no': 1,
            'course_id': COURSE2_ID,
            'teacher_id': TEACHER2_ID,
            'room_id': ROOM2_ID,
            'course_type': 'prac'
        },
        {
            'day': 3,
            'lesson_id': 1,
            'frequency': TimeslotFrequency.ALL,
            'group_id': GROUP3_ID,
            'subgroup_no': 1,
            'course_id': COURSE3_ID,
            'teacher_id': TEACHER3_ID,
            'room_id': ROOM3_ID,
            'course_type': 'lab'
        },
        {
            'day': 5,
            'lesson_id': 3,
            'frequency': TimeslotFrequency.ALL,
            'group_id': GROUP4_ID,
            'subgroup_no': 1,
            'course_id': COURSE2_ID,
            'teacher_id': TEACHER2_ID,
            'room_id': ROOM1_ID,
            'course_type': 'prac'
        },
    ]

    for asg_data in assignments_data:
        # Знаходимо timeslot
        result = await session.execute(
            select(Timeslot).where(
                Timeslot.day == asg_data['day'],
                Timeslot.lesson_id == asg_data['lesson_id'],
                Timeslot.frequency == asg_data['frequency']
            )
        )
        timeslot = result.scalar_one_or_none()
        if not timeslot:
            print(f"⚠️  Помилка: не знайдено timeslot для day={asg_data['day']}, lesson={asg_data['lesson_id']}, freq={asg_data['frequency']}")
            continue

        assignment = Assignment(
            assignment_id=uuid.uuid4(),
            schedule_id=SCHEDULE1_ID,
            timeslot_id=timeslot.timeslot_id,
            group_id=asg_data['group_id'],
            subgroup_no=asg_data['subgroup_no'],
            course_id=asg_data['course_id'],
            teacher_id=asg_data['teacher_id'],
            room_id=asg_data['room_id'],
            course_type=asg_data['course_type']
        )
        session.add(assignment)
    print("✓ Призначення створені")


async def _create_registration_requests(session: AsyncSession):
    """Створює тестові заявки на реєстрацію"""
    requests = [
        RegistrationRequest(
            request_id=uuid.uuid4(),
            google_sub="google_sub_pending_1",
            email="pending@university.edu",
            first_name="Тест",
            last_name="Користувач",
            patronymic="Тестович",
            requested_role=UserRole.STUDENT,
            status=RegistrationStatus.PENDING,
            group_id=GROUP2_ID
        ),
        RegistrationRequest(
            request_id=uuid.uuid4(),
            google_sub="google_sub_approved_1",
            email="approved@university.edu",
            first_name="Схвалений",
            last_name="Користувач",
            patronymic="Тестович",
            requested_role=UserRole.STUDENT,
            status=RegistrationStatus.APPROVED,
            group_id=GROUP3_ID
        ),
    ]
    for req in requests:
        session.add(req)
    print("✓ Заявки на реєстрацію створені")


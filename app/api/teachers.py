from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
import uuid

from app.services.teacher_service import TeacherService
from app.services.course_service import CourseService
from app.services.group_service import GroupService
from app.services.assignment_service import AssignmentService
from app.services.schedule_service import ScheduleService
from app.services.grade_service import GradeService
from app.services.homework_service import HomeworkService
from app.services.attendance_service import AttendanceService
from app.repositories.students_repository import StudentRepository
from app.core.deps import (
    get_teacher_service, get_course_service, get_group_service, get_assignment_service, 
    get_schedule_service, get_student_repository, get_grade_service, get_homework_service,
    get_attendance_service
)
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse, TeacherListResponse
from app.schemas.assignment import AssignmentResponse
from app.schemas.student import StudentOut
from app.schemas.grade import GradeCreate, GradeResponse
from app.schemas.homework import HomeworkCreate, HomeworkSubmissionsResponse
from app.schemas.attendance import AttendanceCreate, AttendanceResponse
from datetime import datetime, date

router = APIRouter()


@router.get("/", response_model=TeacherListResponse)
async def get_all_teachers(
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherListResponse:
    return await teacher_service.get_all_teachers()


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher_by_id(
    teacher_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with id {teacher_id} not found"
        )
    return teacher


@router.get("/user/{user_id}", response_model=TeacherResponse)
async def get_teacher_by_user_id(
    user_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    teacher = await teacher_service.get_teacher_by_user_id(user_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with user_id {user_id} not found"
        )
    return teacher


@router.get("/{teacher_id}/courses", response_model=List[dict])
async def get_teacher_courses(
    teacher_id: uuid.UUID,
    course_service: CourseService = Depends(get_course_service)
) -> List[dict]:
    teacher_service = TeacherService(course_service.repo._session)
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    courses = await course_service.get_courses_by_teacher_id(teacher_id)
    return [course.model_dump() for course in courses]


@router.get("/{teacher_id}/groups", response_model=List[dict])
async def get_teacher_groups(
    teacher_id: uuid.UUID,
    group_service: GroupService = Depends(get_group_service)
) -> List[dict]:
    teacher_service = TeacherService(group_service.repo._session)
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    groups = await group_service.get_groups_by_teacher_id(teacher_id)
    return [group.model_dump() for group in groups]


@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher_data: TeacherCreate,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    try:
        new_teacher = await teacher_service.create_teacher(teacher_data)
        return new_teacher
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create teacher: {str(e)}"
        )


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: uuid.UUID,
    teacher_data: TeacherUpdate,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    teacher = await teacher_service.update_teacher(teacher_id, teacher_data)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with id {teacher_id} not found"
        )
    return teacher


@router.patch("/{teacher_id}/confirm", response_model=TeacherResponse)
async def confirm_teacher(
    teacher_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    teacher = await teacher_service.confirm_teacher(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with id {teacher_id} not found"
        )
    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service)
):
    success = await teacher_service.delete_teacher(teacher_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with id {teacher_id} not found"
        )


@router.get("/{teacher_id}/schedule", response_model=List[AssignmentResponse])
async def get_teacher_schedule(
    teacher_id: uuid.UUID,
    schedule_id: Optional[uuid.UUID] = Query(None, description="Schedule ID. If not provided, returns latest schedule assignments."),
    teacher_service: TeacherService = Depends(get_teacher_service),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    schedule_service: ScheduleService = Depends(get_schedule_service)
) -> List[AssignmentResponse]:
    """
    Отримує розклад конкретного викладача.
    
    Якщо schedule_id не вказано, використовується останній створений розклад.
    """
    # Перевіряємо, чи існує викладач
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    # Якщо schedule_id не вказано, отримуємо останній розклад
    if schedule_id is None:
        try:
            latest_schedule = await schedule_service.get_latest_schedule()
            schedule_id = latest_schedule.schedule_id
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No schedules found"
            )
    
    # Отримуємо призначення для викладача
    assignments = await assignment_service.get_teacher_schedule(
        teacher_id=teacher_id,
        schedule_id=schedule_id
    )
    
    # Конвертуємо в схему відповіді
    return [AssignmentResponse.model_validate(assignment) for assignment in assignments]


@router.get("/{teacher_id}/students", response_model=List[StudentOut])
async def get_teacher_students(
    teacher_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service),
    student_repository: StudentRepository = Depends(get_student_repository)
) -> List[StudentOut]:
    """
    Отримує список студентів (груп) конкретного викладача.
    
    Повертає всіх студентів, які належать до груп, де викладач викладає курси.
    """
    # Перевіряємо, чи існує викладач
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    # Отримуємо студентів викладача
    students = await student_repository.find_by_teacher_id(teacher_id)
    
    # Конвертуємо в схему відповіді
    return [StudentOut.model_validate(student) for student in students]


@router.post("/{teacher_id}/grades", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def create_grade(
    teacher_id: uuid.UUID,
    grade_data: GradeCreate,
    teacher_service: TeacherService = Depends(get_teacher_service),
    grade_service: GradeService = Depends(get_grade_service)
) -> GradeResponse:
    """
    Створює оцінку для студента.
    """
    # Перевіряємо, чи існує викладач
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    # Створюємо оцінку
    grade = await grade_service.create_grade(
        student_id=grade_data.student_id,
        course_id=grade_data.course_id,
        teacher_id=teacher_id,
        points=grade_data.points,
        max_points=grade_data.max_points,
        comment=grade_data.comment,
        classroom_url=grade_data.classroom_url,
    )
    
    return GradeResponse(
        id=str(grade.grade_id),
        studentId=str(grade.student_id),
        courseId=str(grade.course_id),
        teacherId=str(grade.teacher_id),
        points=float(grade.points),
        maxPoints=float(grade.max_points) if grade.max_points else None,
        comment=grade.comment,
        classroomUrl=grade.classroom_url,
        createdAt=grade.created_at.isoformat() if grade.created_at else "",
    )


@router.post("/{teacher_id}/homework", status_code=status.HTTP_201_CREATED)
async def create_homework(
    teacher_id: uuid.UUID,
    homework_data: HomeworkCreate,
    teacher_service: TeacherService = Depends(get_teacher_service),
    homework_service: HomeworkService = Depends(get_homework_service)
):
    """
    Створює домашнє завдання для вказаних груп.
    """
    # Перевіряємо, чи існує викладач
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    # Парсимо дату
    try:
        due_date = datetime.fromisoformat(homework_data.due_date.replace('Z', '+00:00')).date()
    except:
        due_date = datetime.strptime(homework_data.due_date, "%Y-%m-%d").date()
    
    # Створюємо домашнє завдання
    attachments = None
    if homework_data.attachments:
        attachments = [{"url": a.url, "title": a.title} for a in homework_data.attachments]
    
    created_homework = await homework_service.create_homework_for_groups(
        course_id=homework_data.course_id,
        group_ids=homework_data.group_ids,
        teacher_id=teacher_id,
        text=f"{homework_data.title}\n\n{homework_data.description}",
        due_date=due_date,
        attachments=attachments,
    )
    
    return {
        "message": f"Homework created for {len(created_homework)} students",
        "count": len(created_homework),
    }


@router.get("/{teacher_id}/homework")
async def get_teacher_homework(
    teacher_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service),
    homework_service: HomeworkService = Depends(get_homework_service)
):
    """
    Отримує всі домашні завдання викладача.
    """
    # Перевіряємо, чи існує викладач
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    # Отримуємо домашні завдання
    homework_data = await homework_service.get_teacher_homework(teacher_id)
    
    return homework_data


@router.get("/{teacher_id}/homework/{homework_id}/submissions", response_model=HomeworkSubmissionsResponse)
async def get_homework_submissions(
    teacher_id: uuid.UUID,
    homework_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service),
    homework_service: HomeworkService = Depends(get_homework_service)
) -> HomeworkSubmissionsResponse:
    """
    Отримує всі відправки для конкретного домашнього завдання.
    """
    # Перевіряємо, чи існує викладач
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    # Отримуємо відправки
    submissions_data = await homework_service.get_homework_submissions(homework_id)
    
    return HomeworkSubmissionsResponse.model_validate(submissions_data)


@router.post("/{teacher_id}/lessons/{assignment_id}/attendance", status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    teacher_id: uuid.UUID,
    assignment_id: uuid.UUID,
    attendance_data: AttendanceCreate,
    teacher_service: TeacherService = Depends(get_teacher_service),
    attendance_service: AttendanceService = Depends(get_attendance_service)
):
    """
    Відмічає присутність студентів на занятті.
    """
    # Перевіряємо, чи існує викладач
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    # Парсимо дату
    try:
        attendance_date = datetime.fromisoformat(attendance_data.date.replace('Z', '+00:00')).date()
    except:
        attendance_date = datetime.strptime(attendance_data.date, "%Y-%m-%d").date()
    
    # Підготовлюємо дані студентів
    students_data = [
        {
            "student_id": str(student.student_id),
            "status": student.status,
            "note": student.note,
        }
        for student in attendance_data.students
    ]
    
    # Відмічаємо присутність
    attendances = await attendance_service.mark_attendance(
        assignment_id=assignment_id,
        attendance_date=attendance_date,
        students=students_data,
    )
    
    return {
        "message": f"Attendance marked for {len(attendances)} students",
        "count": len(attendances),
    }
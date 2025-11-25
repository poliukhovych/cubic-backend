from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
import uuid

from app.repositories.students_repository import StudentRepository
from app.services.assignment_service import AssignmentService
from app.services.schedule_service import ScheduleService
from app.services.grade_service import GradeService
from app.services.homework_service import HomeworkService
from app.services.attendance_service import AttendanceService
from app.core.deps import (
    get_student_repository, 
    get_assignment_service, 
    get_schedule_service,
    get_grade_service,
    get_homework_service,
    get_attendance_service
)
from app.schemas.student import StudentOut
from app.schemas.assignment import AssignmentResponse
from app.schemas.grade import StudentGradesResponse
from app.schemas.homework import StudentHomeworkResponse, HomeworkSubmissionCreate, HomeworkSubmissionResponse
from app.schemas.attendance import AttendanceListResponse
from datetime import datetime, date

router = APIRouter()


@router.get("/user/{user_id}", response_model=StudentOut)
async def get_student_by_user_id(
    user_id: uuid.UUID,
    student_repository: StudentRepository = Depends(get_student_repository)
) -> StudentOut:
    """
    Отримує студента за user_id.
    """
    student = await student_repository.find_by_user_id(user_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with user_id {user_id} not found"
        )
    return StudentOut.model_validate(student)


@router.get("/{student_id}/schedule", response_model=List[AssignmentResponse])
async def get_student_schedule(
    student_id: uuid.UUID,
    schedule_id: Optional[uuid.UUID] = Query(None, description="Schedule ID. If not provided, returns latest schedule assignments."),
    student_repository: StudentRepository = Depends(get_student_repository),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    schedule_service: ScheduleService = Depends(get_schedule_service)
) -> List[AssignmentResponse]:
    """
    Отримує розклад конкретного студента.
    
    Якщо schedule_id не вказано, використовується останній створений розклад.
    """
    # Перевіряємо, чи існує студент
    student = await student_repository.find_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    # Перевіряємо, чи у студента є група
    if not student.group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student {student_id} is not assigned to any group"
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
    
    # Отримуємо призначення для групи студента
    assignments = await assignment_service.get_student_schedule(
        group_id=student.group_id,
        schedule_id=schedule_id
    )
    
    # Конвертуємо в схему відповіді
    return [AssignmentResponse.model_validate(assignment) for assignment in assignments]


@router.get("/{student_id}/grades", response_model=StudentGradesResponse)
async def get_student_grades(
    student_id: uuid.UUID,
    course_id: Optional[uuid.UUID] = Query(None, description="Filter by course ID"),
    student_repository: StudentRepository = Depends(get_student_repository),
    grade_service: GradeService = Depends(get_grade_service)
) -> StudentGradesResponse:
    """
    Отримує оцінки конкретного студента.
    
    Повертає оцінки, згруповані за предметами.
    Можна фільтрувати за course_id.
    """
    # Перевіряємо, чи існує студент
    student = await student_repository.find_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    # Отримуємо оцінки (з фільтром за course_id, якщо вказано)
    grades_data = await grade_service.get_student_grades(student_id, course_id=course_id)
    
    return StudentGradesResponse.model_validate(grades_data)


@router.get("/{student_id}/homework", response_model=StudentHomeworkResponse)
async def get_student_homework(
    student_id: uuid.UUID,
    status: Optional[str] = Query(None, description="Filter by status: pending, completed, overdue"),
    student_repository: StudentRepository = Depends(get_student_repository),
    homework_service: HomeworkService = Depends(get_homework_service)
) -> StudentHomeworkResponse:
    """
    Отримує домашні завдання конкретного студента.
    
    Повертає список домашніх завдань з можливістю фільтрації за статусом.
    """
    # Перевіряємо, чи існує студент
    student = await student_repository.find_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    # Визначаємо include_done на основі статусу
    include_done = True
    if status == "pending":
        include_done = False
    
    # Отримуємо домашні завдання
    homework_data = await homework_service.get_student_homework(
        student_id, 
        include_done=include_done
    )
    
    # Фільтруємо за статусом, якщо вказано
    if status == "overdue":
        today = date.today()
        homework_data["tasks"] = [
            task for task in homework_data["tasks"]
            if not task.get("done", False) and task.get("dueDate") and datetime.fromisoformat(task["dueDate"]).date() < today
        ]
    elif status == "completed":
        homework_data["tasks"] = [
            task for task in homework_data["tasks"]
            if task.get("done", False)
        ]
    
    return StudentHomeworkResponse.model_validate(homework_data)


@router.post("/{student_id}/homework/{homework_id}/submit", response_model=HomeworkSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_homework(
    student_id: uuid.UUID,
    homework_id: uuid.UUID,
    submission_data: HomeworkSubmissionCreate,
    student_repository: StudentRepository = Depends(get_student_repository),
    homework_service: HomeworkService = Depends(get_homework_service)
) -> HomeworkSubmissionResponse:
    """
    Відправляє домашнє завдання студентом.
    """
    # Перевіряємо, чи існує студент
    student = await student_repository.find_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    # Підготовлюємо вкладення
    attachments = None
    if submission_data.attachments:
        attachments = [{"url": a.url, "title": a.title} for a in submission_data.attachments]
    
    # Відправляємо домашнє завдання
    try:
        submission = await homework_service.submit_homework(
            homework_id=homework_id,
            student_id=student_id,
            content=submission_data.content,
            attachments=attachments,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Отримуємо файли
    files = []
    if homework_service.submission_repo:
        files_list = await homework_service.submission_repo.find_files_by_submission_id(submission.submission_id)
        files = [
            {
                "id": str(f.file_id),
                "url": f.url,
                "title": f.title,
            }
            for f in files_list
        ]
    
    return HomeworkSubmissionResponse(
        id=str(submission.submission_id),
        homeworkId=str(submission.homework_id),
        studentId=str(submission.student_id),
        content=submission.content,
        submittedAt=submission.submitted_at.isoformat() if submission.submitted_at else "",
        grade=float(submission.grade) if submission.grade else None,
        feedback=submission.feedback,
        files=files,
    )


@router.get("/{student_id}/attendance", response_model=AttendanceListResponse)
async def get_student_attendance(
    student_id: uuid.UUID,
    course_id: Optional[uuid.UUID] = Query(None, description="Filter by course ID"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    student_repository: StudentRepository = Depends(get_student_repository),
    attendance_service: AttendanceService = Depends(get_attendance_service)
) -> AttendanceListResponse:
    """
    Отримує відвідуваність конкретного студента.
    
    Можна фільтрувати за course_id та діапазоном дат.
    """
    # Перевіряємо, чи існує студент
    student = await student_repository.find_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    # Парсимо дати
    from_date_obj = None
    to_date_obj = None
    if from_date:
        try:
            from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00')).date()
        except:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
    if to_date:
        try:
            to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00')).date()
        except:
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
    
    # Отримуємо відвідуваність
    attendances = await attendance_service.get_student_attendance(
        student_id=student_id,
        course_id=course_id,
        from_date=from_date_obj,
        to_date=to_date_obj,
    )
    
    return AttendanceListResponse(attendances=attendances)


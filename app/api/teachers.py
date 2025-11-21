from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
import uuid

from app.services.teacher_service import TeacherService
from app.services.course_service import CourseService
from app.services.group_service import GroupService
from app.services.assignment_service import AssignmentService
from app.services.schedule_service import ScheduleService
from app.core.deps import get_teacher_service, get_course_service, get_group_service, get_assignment_service, get_schedule_service
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse, TeacherListResponse
from app.schemas.assignment import AssignmentResponse

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
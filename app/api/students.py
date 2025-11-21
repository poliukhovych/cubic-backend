from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
import uuid

from app.repositories.students_repository import StudentRepository
from app.services.assignment_service import AssignmentService
from app.services.schedule_service import ScheduleService
from app.core.deps import get_student_repository, get_assignment_service, get_schedule_service
from app.schemas.student import StudentOut
from app.schemas.assignment import AssignmentResponse

router = APIRouter()


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


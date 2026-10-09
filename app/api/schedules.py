from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from uuid import UUID

from app.core.deps import get_schedule_generation_service, get_schedule_service, get_assignment_service
from app.core.security import get_current_user, get_current_admin
from app.schemas.schedule import (
    ScheduleGenerationResponse,
    ScheduleResponse,
    ScheduleListResponse,
    ScheduleDetailsResponse,
    ReplaceAssignmentsRequest,
)
from app.services.schedule_generation_service import ScheduleGenerationService
from app.services.schedule_service import ScheduleService
from app.services.assignment_service import AssignmentService
from sqlalchemy.exc import NoResultFound

router = APIRouter(
    prefix="/schedules",
    dependencies=[Depends(get_current_user)],
)


class ScheduleGenerationRequest(BaseModel):
    policy: Dict[str, Any] = {}
    params: Dict[str, Any] = {}
    schedule_label: str = "Generated Schedule"


@router.post("/generate", response_model=ScheduleGenerationResponse, dependencies=[Depends(get_current_admin)])
async def generate_new_schedule(
    request: ScheduleGenerationRequest,
    service: ScheduleGenerationService = Depends(get_schedule_generation_service)
):
    """
    Запускає генерацію нового розкладу.

    Цей ендпоінт звертається до ScheduleGenerationService, який виконує всю
    важку роботу:
    1. Збирає дані з локальної БД.
    2. Відправляє їх мікросервісу планування.
    3. Очікує на результат.
    4. Зберігає готовий розклад назад у локальну БД.
    """
    try:
        saved_assignments = await service.generate_and_save_schedule(
            policy=request.policy,
            params=request.params,
            schedule_label=request.schedule_label
        )
        return {
            "message": f"Successfully generated and saved a new schedule with {len(saved_assignments)} assignments.",
            "schedule": saved_assignments
        }

    except HTTPException:
        raise
    except Exception as e:
        # Обробити специфічні помилки сервісу
        print(f"Error during schedule generation: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.get("/", response_model=ScheduleListResponse)
async def list_schedules(
    service: ScheduleService = Depends(get_schedule_service)
):
    """Усі розклади, найновіші першими."""
    schedules = await service.get_all_schedules()
    return ScheduleListResponse(
        schedules=[ScheduleResponse.model_validate(s) for s in schedules],
        total=len(schedules),
    )


@router.get("/active", response_model=ScheduleDetailsResponse)
async def get_active_schedule(
    service: ScheduleService = Depends(get_schedule_service),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    """Активний розклад (або останній, якщо активного немає) з усіма заняттями."""
    try:
        schedule = await service.get_current_schedule()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="No schedules found")
    return ScheduleDetailsResponse(
        schedule=ScheduleResponse.model_validate(schedule),
        assignments=await assignment_service.get_schedule_details(schedule.schedule_id),
    )


@router.get("/latest", response_model=ScheduleResponse)
async def get_latest_schedule(
    service: ScheduleService = Depends(get_schedule_service)
):
    """
    Отримує останній створений розклад.
    
    Повертає розклад з найбільш пізньою датою створення.
    """
    try:
        schedule = await service.get_latest_schedule()
        return ScheduleResponse.model_validate(schedule)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="No schedules found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule_by_id(
    schedule_id: UUID,
    service: ScheduleService = Depends(get_schedule_service)
):
    """
    Отримує розклад за його ID.
    
    Args:
        schedule_id: UUID розкладу, який потрібно отримати
    """
    try:
        schedule = await service.get_schedule_by_id(schedule_id)
        return ScheduleResponse.model_validate(schedule)
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/{schedule_id}/details", response_model=ScheduleDetailsResponse)
async def get_schedule_details(
    schedule_id: UUID,
    service: ScheduleService = Depends(get_schedule_service),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    """Розклад за ID з усіма заняттями."""
    try:
        schedule = await service.get_schedule_by_id(schedule_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    return ScheduleDetailsResponse(
        schedule=ScheduleResponse.model_validate(schedule),
        assignments=await assignment_service.get_schedule_details(schedule_id),
    )


@router.put("/{schedule_id}/assignments", response_model=ScheduleDetailsResponse, dependencies=[Depends(get_current_admin)])
async def replace_schedule_assignments(
    schedule_id: UUID,
    body: ReplaceAssignmentsRequest,
    service: ScheduleService = Depends(get_schedule_service),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    """Зберігає ручні зміни розкладу: повністю замінює заняття (422 — невідомі id, 409 — накладки)."""
    try:
        schedule = await service.get_schedule_by_id(schedule_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    await assignment_service.replace_schedule_assignments(schedule_id, body.assignments)
    return ScheduleDetailsResponse(
        schedule=ScheduleResponse.model_validate(schedule),
        assignments=await assignment_service.get_schedule_details(schedule_id),
    )


@router.post("/{schedule_id}/reoptimize", response_model=ScheduleGenerationResponse, dependencies=[Depends(get_current_admin)])
async def reoptimize_schedule(
    schedule_id: UUID,
    request: ScheduleGenerationRequest,
    service: ScheduleService = Depends(get_schedule_service),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    generation_service: ScheduleGenerationService = Depends(get_schedule_generation_service),
):
    """Новий розклад на основі цього: закріплені (pinned) пари лишаються на місці, решта перераховується."""
    try:
        await service.get_schedule_by_id(schedule_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    pinned = [a for a in await assignment_service.repo.find_by_schedule_id(schedule_id) if a.pinned]
    try:
        saved = await generation_service.generate_and_save_schedule(
            policy=request.policy,
            params=request.params,
            schedule_label=request.schedule_label,
            pinned=pinned,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    return {
        "message": f"Reoptimized: {len(saved)} assignments, {len(pinned)} pinned kept.",
        "schedule": saved,
    }


@router.patch("/{schedule_id}/activate", response_model=ScheduleResponse, dependencies=[Depends(get_current_admin)])
async def activate_schedule(
    schedule_id: UUID,
    service: ScheduleService = Depends(get_schedule_service),
):
    """Робить розклад активним (саме його бачать студенти й викладачі)."""
    try:
        schedule = await service.activate_schedule(schedule_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    return ScheduleResponse.model_validate(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin)])
async def delete_schedule(
    schedule_id: UUID,
    service: ScheduleService = Depends(get_schedule_service),
):
    """Видаляє розклад разом із заняттями. Активний розклад видалити не можна (409)."""
    try:
        await service.delete_schedule(schedule_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from uuid import UUID
import logging

from app.core.deps import get_schedule_generation_service, get_schedule_service, get_assignment_service
from app.schemas.schedule import (
    ScheduleGenerationResponse, 
    ScheduleResponse, 
    ScheduleListResponse,
    ScheduleDetailsResponse
)
from app.schemas.assignment import AssignmentResponse
from app.services.schedule_generation_service import ScheduleGenerationService
from app.services.schedule_service import ScheduleService
from app.services.assignment_service import AssignmentService
from sqlalchemy.exc import NoResultFound

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/schedules"
)


class ScheduleGenerationRequest(BaseModel):
    policy: Dict[str, Any] = {}
    params: Dict[str, Any] = {}
    schedule_label: str = "Generated Schedule"


@router.post("/generate", response_model=ScheduleGenerationResponse)
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

    except Exception as e:
        # Обробити специфічні помилки сервісу
        print(f"Error during schedule generation: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


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


@router.get("/", response_model=ScheduleListResponse)
async def get_all_schedules(
    service: ScheduleService = Depends(get_schedule_service)
):
    """
    Отримує список всіх розкладів.
    
    Повертає всі розклади, відсортовані за датою створення (найновіші спочатку).
    """
    try:
        schedules = await service.get_all_schedules()
        schedule_responses = [ScheduleResponse.model_validate(s) for s in schedules]
        return ScheduleListResponse(
            schedules=schedule_responses,
            total=len(schedule_responses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/{schedule_id}/details", response_model=ScheduleDetailsResponse)
async def get_schedule_details(
    schedule_id: UUID,
    schedule_service: ScheduleService = Depends(get_schedule_service),
    assignment_service: AssignmentService = Depends(get_assignment_service)
):
    """
    Отримує детальну інформацію про розклад, включаючи всі призначення.
    
    Args:
        schedule_id: UUID розкладу, який потрібно отримати
    """
    try:
        schedule = await schedule_service.get_schedule_by_id(schedule_id)
        assignments = await assignment_service.get_assignments_by_schedule_id(schedule_id)
        
        assignment_responses = [AssignmentResponse.model_validate(a) for a in assignments]
        
        schedule_response = ScheduleResponse.model_validate(schedule)
        return ScheduleDetailsResponse(
            **schedule_response.model_dump(),
            assignments=assignment_responses,
            assignments_count=len(assignment_responses)
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/{schedule_id}/activate", response_model=ScheduleResponse)
async def activate_schedule(
    schedule_id: UUID,
    service: ScheduleService = Depends(get_schedule_service)
):
    """
    Активує розклад та деактивує всі інші.
    
    Тільки один розклад може бути активним одночасно.
    При активації нового розкладу всі інші автоматично деактивуються.
    
    Args:
        schedule_id: UUID розкладу, який потрібно активувати
    """
    try:
        schedule = await service.activate_schedule(schedule_id)
        return ScheduleResponse.model_validate(schedule)
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    schedule_service: ScheduleService = Depends(get_schedule_service),
    assignment_service: AssignmentService = Depends(get_assignment_service)
):
    """
    Видаляє розклад та всі його призначення.
    
    Args:
        schedule_id: UUID розкладу, який потрібно видалити
    """
    try:
        # Перевіряємо, чи існує розклад
        await schedule_service.get_schedule_by_id(schedule_id)
        
        # Видаляємо всі призначення для цього розкладу
        from app.repositories.assignment_repository import AssignmentRepository
        from app.db.session import async_session_maker
        async with async_session_maker() as session:
            assignment_repo = AssignmentRepository(session)
            deleted_count = await assignment_repo.delete_by_schedule_id(schedule_id)
            logger.info(f"Видалено призначень: {deleted_count}")
            await session.commit()
        
        # Видаляємо розклад
        deleted = await schedule_service.delete_schedule(schedule_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
        
        return None
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/{schedule_id}/optimize", response_model=ScheduleGenerationResponse)
async def optimize_schedule(
    schedule_id: UUID,
    request: ScheduleGenerationRequest,
    schedule_service: ScheduleService = Depends(get_schedule_service),
    generation_service: ScheduleGenerationService = Depends(get_schedule_generation_service),
    assignment_service: AssignmentService = Depends(get_assignment_service)
):
    """
    Оптимізує існуючий розклад.
    
    Використовує поточні призначення як базові та застосовує оптимізацію
    з новими параметрами та політиками.
    
    Args:
        schedule_id: UUID розкладу, який потрібно оптимізувати
        request: Параметри оптимізації (policy, params)
    """
    try:
        # Перевіряємо, чи існує розклад
        schedule = await schedule_service.get_schedule_by_id(schedule_id)
        
        # Отримуємо поточні призначення
        assignments = await assignment_service.get_assignments_by_schedule_id(schedule_id)
        
        if not assignments:
            raise HTTPException(
                status_code=400, 
                detail=f"Schedule {schedule_id} has no assignments to optimize"
            )
        
        # Викликаємо метод оптимізації
        saved_assignments = await generation_service.reoptimize_schedule(
            schedule_id=schedule_id,
            policy=request.policy,
            params=request.params,
            existing_assignments=assignments
        )
        
        return {
            "message": f"Successfully optimized schedule with {len(saved_assignments)} assignments.",
            "schedule": saved_assignments
        }
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Schedule with id {schedule_id} not found")
    except HTTPException:
        raise
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

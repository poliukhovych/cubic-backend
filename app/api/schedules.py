from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from uuid import UUID

from app.core.deps import get_schedule_generation_service, get_schedule_service
from app.schemas.schedule import ScheduleGenerationResponse, ScheduleResponse
from app.services.schedule_generation_service import ScheduleGenerationService
from app.services.schedule_service import ScheduleService
from sqlalchemy.exc import NoResultFound

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

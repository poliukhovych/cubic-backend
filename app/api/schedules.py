from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_schedule_service
from app.schemas.schedule import ScheduleGenerationResponse
from app.services.schedule_generation_service import ScheduleService

router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"]
)


@router.post("/generate", response_model=ScheduleGenerationResponse)
async def generate_new_schedule(
    service: ScheduleService = Depends(get_schedule_service)
):
    """
    Запускає генерацію нового розкладу.

    Цей ендпоінт звертається до ScheduleService, який виконує всю
    важку роботу:
    1. Збирає дані з локальної БД.
    2. Відправляє їх мікросервісу планування.
    3. Очікує на результат.
    4. Зберігає готовий розклад назад у локальну БД.
    """
    try:
        saved_assignments = await service.generate_and_save_schedule()
        return {
            "message": f"Successfully generated and saved a new schedule with {len(saved_assignments)} assignments.",
            "schedule": saved_assignments
        }

    except Exception as e:
        # Обробити специфічні помилки сервісу
        print(f"Error during schedule generation: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

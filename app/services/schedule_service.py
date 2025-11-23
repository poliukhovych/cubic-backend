import logging
from datetime import datetime
from app.repositories.schedule_repository import ScheduleRepository
from app.db.models.scheduling.schedule import Schedule
from uuid import UUID
from sqlalchemy.exc import NoResultFound

logger = logging.getLogger(__name__)

class ScheduleService:
    """
    Service for simple CRUD operations on the 'schedules' (parent) table.
    """
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    async def create_schedule(self, label: str) -> Schedule:
        """
        Creates a new schedule with the given label.
        If a schedule with the same label already exists, appends a timestamp to make it unique.
        """
        logger.info(f"Створення розкладу в БД: label='{label}'")
        
        # Check if a schedule with this label already exists
        existing_schedule = await self.repo.find_by_label(label)
        if existing_schedule:
            # Append timestamp to make the label unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_label = f"{label} ({timestamp})"
            logger.info(f"Розклад з label='{label}' вже існує. Використовуємо унікальний label: '{unique_label}'")
            label = unique_label
        
        schedule = await self.repo.create(label=label)
        logger.info(f"Розклад створено в БД: schedule_id={schedule.schedule_id}, label='{schedule.label}', created_at={schedule.created_at}")
        return schedule

    async def get_schedule_by_id(self, schedule_id: UUID) -> Schedule:
        schedule = await self.repo.find_by_id(schedule_id)
        if not schedule:
            raise NoResultFound("Schedule not found")
        return schedule

    async def get_latest_schedule(self) -> Schedule:
        """Get the most recently created schedule."""
        schedule = await self.repo.find_latest()
        if not schedule:
            raise NoResultFound("No schedules found")
        return schedule

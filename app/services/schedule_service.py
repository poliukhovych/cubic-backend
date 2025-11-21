import logging
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
        logger.info(f"Створення розкладу в БД: label='{label}'")
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

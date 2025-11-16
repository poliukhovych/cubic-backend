from app.repositories.schedule_repository import ScheduleRepository
from app.db.models.scheduling.schedule import Schedule
from uuid import UUID
from sqlalchemy.exc import NoResultFound

class ScheduleService:
    """
    Service for simple CRUD operations on the 'schedules' (parent) table.
    """
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    async def create_schedule(self, label: str) -> Schedule:
        return await self.repo.create(label=label)

    async def get_schedule_by_id(self, schedule_id: UUID) -> Schedule:
        schedule = await self.repo.find_by_id(schedule_id)
        if not schedule:
            raise NoResultFound("Schedule not found")
        return schedule

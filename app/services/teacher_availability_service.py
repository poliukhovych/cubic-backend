from uuid import UUID
from typing import List

from app.repositories.availability_repository import AvailabilityRepository
from app.services.timeslot_service import TimeslotService


class TeacherAvailabilityService:
    """
    Service for managing teacher availability.
    """

    def __init__(
            self,
            availability_repo: AvailabilityRepository,
            timeslot_service: TimeslotService
    ):
        self.repo = availability_repo
        self.timeslot_service = timeslot_service

    async def get_teacher_availability_ids(self, teacher_id: UUID) -> List[str]:
        """
        Returns a list of formatted timeslot strings (e.g., 'mon.all.1')
        that the teacher is available for.
        """
        # 1. Get raw DB IDs
        db_ids = await self.repo.get_teacher_availability(teacher_id)

        # 2. Get map to convert to strings
        id_map = await self.timeslot_service.get_id_map()

        # 3. Convert
        return [id_map[tid] for tid in db_ids if tid in id_map]

    async def set_availability(self, teacher_id: UUID, timeslot_ids: List[int]):
        """
        Updates the availability for a teacher.
        """
        await self.repo.set_teacher_availability(teacher_id, timeslot_ids)

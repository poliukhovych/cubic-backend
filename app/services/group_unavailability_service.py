from uuid import UUID
from typing import List

from app.repositories.availability_repository import AvailabilityRepository
from app.services.timeslot_service import TimeslotService

class GroupUnavailabilityService:
    """
    Service for managing group unavailability (blocked slots).
    """
    def __init__(
        self,
        availability_repo: AvailabilityRepository,
        timeslot_service: TimeslotService
    ):
        self.repo = availability_repo
        self.timeslot_service = timeslot_service

    async def get_group_unavailability_ids(self, group_id: UUID) -> List[str]:
        """
        Returns a list of formatted timeslot strings that the group
        is UNAVAILABLE for.
        """
        db_ids = await self.repo.get_group_unavailability(group_id)
        id_map = await self.timeslot_service.get_id_map()
        return [id_map[tid] for tid in db_ids if tid in id_map]

from uuid import UUID
from typing import List
from app.repositories.constraint_repository import ConstraintRepository
from app.db.models.scheduling.subgroup_constraints import SubgroupConstraints

class SubgroupConstraintService:
    """
    Service for accessing subgroup constraints.
    Used to determine if a group needs to be split for a specific course.
    """
    def __init__(self, repo: ConstraintRepository):
        self.repo = repo

    async def get_constraints_by_schedule(self, schedule_id: UUID) -> List[SubgroupConstraints]:
        """
        Returns constraints relevant to a specific schedule context.
        """
        return await self.repo.get_subgroup_constraints(schedule_id)

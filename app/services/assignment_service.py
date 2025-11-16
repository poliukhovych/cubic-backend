from app.repositories.assignment_repository import AssignmentRepository
from app.db.models.scheduling.assignment import Assignment
from app.schemas.assignment import AssignmentCreate
from typing import List, Dict, Any
from uuid import UUID


class AssignmentService:
    """
    Service for saving the schedule results ('assignments') to the DB.
    """

    def __init__(self, repo: AssignmentRepository):
        self.repo = repo

    async def create_assignments(
            self, schedule_id: UUID, assignments_data: List[Dict[str, Any]]
    ) -> List[Assignment]:
        """
        Transforms raw assignment data and bulk-creates all
        assignment records for a given schedule ID.
        """

        # 1. Prepare the list of Pydantic models
        assignments_to_create: List[AssignmentCreate] = []
        for raw_assignment in assignments_data:
            # Combine the schedule_id with the rest of the data
            data_with_id = {
                **raw_assignment,
                "schedule_id": schedule_id
            }
            # Validate the data using the schema
            assignments_to_create.append(AssignmentCreate(**data_with_id))

        # 2. Call the repository with the correct single argument
        if not assignments_to_create:
            return []

        return await self.repo.bulk_create(
            assignments=assignments_to_create
        )

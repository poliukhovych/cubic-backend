import logging
import json
from app.repositories.assignment_repository import AssignmentRepository
from app.db.models.scheduling.assignment import Assignment
from app.schemas.assignment import AssignmentCreate
from typing import List, Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)


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
        logger.info(f"Початок збереження призначень в БД для schedule_id={schedule_id}")
        logger.info(f"Кількість призначень для збереження: {len(assignments_data)}")

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
            logger.warning("Немає призначень для збереження")
            return []

        logger.debug(f"Дані призначень для запису в БД: {json.dumps([a.model_dump() for a in assignments_to_create], ensure_ascii=False, indent=2, default=str)}")
        
        saved_assignments = await self.repo.bulk_create(
            assignments=assignments_to_create
        )
        
        logger.info(f"Успішно збережено в БД призначень: {len(saved_assignments)}")
        logger.debug(f"Деталі збережених призначень: {[{'assignment_id': str(a.assignment_id), 'schedule_id': str(a.schedule_id), 'group_id': str(a.group_id), 'course_id': str(a.course_id), 'teacher_id': str(a.teacher_id)} for a in saved_assignments]}")
        
        return saved_assignments

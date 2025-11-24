import logging
import json
from app.repositories.assignment_repository import AssignmentRepository
from app.db.models.scheduling.assignment import Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.exc import NoResultFound

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

    async def get_teacher_schedule(
            self, teacher_id: UUID, schedule_id: Optional[UUID] = None
    ) -> List[Assignment]:
        """
        Gets all assignments for a specific teacher.
        If schedule_id is provided, returns assignments for that schedule only.
        Otherwise, returns all assignments for the teacher across all schedules.
        """
        if schedule_id:
            logger.info(f"Отримання розкладу викладача {teacher_id} для розкладу {schedule_id}")
            assignments = await self.repo.find_by_schedule_and_teacher(
                schedule_id=schedule_id,
                teacher_id=teacher_id
            )
        else:
            logger.info(f"Отримання всіх розкладів викладача {teacher_id}")
            assignments = await self.repo.find_by_teacher_id(teacher_id)
        
        logger.info(f"Знайдено призначень: {len(assignments)}")
        return assignments

    async def get_student_schedule(
            self, group_id: UUID, schedule_id: Optional[UUID] = None
    ) -> List[Assignment]:
        """
        Gets all assignments for a specific student's group.
        If schedule_id is provided, returns assignments for that schedule only.
        Otherwise, returns all assignments for the group across all schedules.
        """
        if schedule_id:
            logger.info(f"Отримання розкладу групи {group_id} для розкладу {schedule_id}")
            assignments = await self.repo.find_by_schedule_and_group(
                schedule_id=schedule_id,
                group_id=group_id
            )
        else:
            logger.info(f"Отримання всіх розкладів групи {group_id}")
            assignments = await self.repo.find_by_group_id(group_id)
        
        logger.info(f"Знайдено призначень: {len(assignments)}")
        return assignments

    async def get_assignments_by_schedule_id(self, schedule_id: UUID) -> List[Assignment]:
        """Gets all assignments for a specific schedule."""
        logger.info(f"Отримання всіх призначень для розкладу {schedule_id}")
        assignments = await self.repo.find_by_schedule_id(schedule_id)
        logger.info(f"Знайдено призначень: {len(assignments)}")
        return assignments

    async def get_assignment_by_id(self, assignment_id: UUID) -> Assignment:
        """Gets a single assignment by its ID."""
        assignment = await self.repo.find_by_id(assignment_id)
        if not assignment:
            raise NoResultFound(f"Assignment with id {assignment_id} not found")
        return assignment

    async def create_assignment(
            self, 
            schedule_id: UUID, 
            assignment_data: Dict[str, Any]
    ) -> Assignment:
        """
        Creates a single assignment for a given schedule.
        
        Args:
            schedule_id: UUID of the schedule
            assignment_data: Dictionary with assignment fields (timeslotId, groupId, etc.)
        
        Returns:
            Created Assignment model
        """
        logger.info(f"Створення призначення для розкладу {schedule_id}")
        
        # Ensure schedule_id is set
        data_with_schedule = {
            **assignment_data,
            "scheduleId": schedule_id
        }
        
        # Validate using schema
        assignment_create = AssignmentCreate(**data_with_schedule)
        
        # Create in repository
        assignment = await self.repo.create(
            schedule_id=assignment_create.schedule_id,
            timeslot_id=assignment_create.timeslot_id,
            group_id=assignment_create.group_id,
            subgroup_no=assignment_create.subgroup_no,
            course_id=assignment_create.course_id,
            teacher_id=assignment_create.teacher_id,
            room_id=assignment_create.room_id,
            course_type=assignment_create.course_type
        )
        
        logger.info(f"Створено призначення: assignment_id={assignment.assignment_id}")
        return assignment

    async def update_assignment(
            self,
            assignment_id: UUID,
            assignment_data: Dict[str, Any]
    ) -> Assignment:
        """
        Updates an existing assignment.
        
        Args:
            assignment_id: UUID of the assignment to update
            assignment_data: Dictionary with fields to update (all optional)
        
        Returns:
            Updated Assignment model
        """
        logger.info(f"Оновлення призначення {assignment_id}")
        
        # Validate using schema (all fields optional)
        assignment_update = AssignmentUpdate(**assignment_data)
        
        # Convert to repository format (using UNSET for None values)
        from app.utils.unset import UNSET
        
        update_kwargs = {}
        if assignment_update.timeslot_id is not None:
            update_kwargs["timeslot_id"] = assignment_update.timeslot_id
        if assignment_update.group_id is not None:
            update_kwargs["group_id"] = assignment_update.group_id
        if assignment_update.subgroup_no is not None:
            update_kwargs["subgroup_no"] = assignment_update.subgroup_no
        if assignment_update.course_id is not None:
            update_kwargs["course_id"] = assignment_update.course_id
        if assignment_update.teacher_id is not None:
            update_kwargs["teacher_id"] = assignment_update.teacher_id
        if assignment_update.room_id is not None:
            update_kwargs["room_id"] = assignment_update.room_id
        elif "roomId" in assignment_data and assignment_data["roomId"] is None:
            # Explicitly set to None if provided as null
            update_kwargs["room_id"] = None
        if assignment_update.course_type is not None:
            update_kwargs["course_type"] = assignment_update.course_type
        
        # Update in repository
        updated_assignment = await self.repo.update(
            assignment_id=assignment_id,
            **update_kwargs
        )
        
        if not updated_assignment:
            raise NoResultFound(f"Assignment with id {assignment_id} not found")
        
        logger.info(f"Оновлено призначення: assignment_id={updated_assignment.assignment_id}")
        return updated_assignment

    async def delete_assignment(self, assignment_id: UUID) -> bool:
        """
        Deletes an assignment by its ID.
        
        Args:
            assignment_id: UUID of the assignment to delete
        
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Видалення призначення {assignment_id}")
        
        # Check if exists first
        exists = await self.repo.exists(assignment_id)
        if not exists:
            raise NoResultFound(f"Assignment with id {assignment_id} not found")
        
        deleted = await self.repo.delete(assignment_id)
        logger.info(f"Призначення {assignment_id} {'видалено' if deleted else 'не видалено'}")
        return deleted

import logging
import json
from collections import defaultdict
from app.repositories.assignment_repository import AssignmentRepository
from app.db.models.scheduling.assignment import Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentDetails, MicroserviceAssignment
from app.core.exceptions import ValidationError, ConflictError
from typing import List, Dict, Any, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class AssignmentService:
    """
    Service for saving the schedule results ('assignments') to the DB.
    """

    def __init__(self, repo: AssignmentRepository):
        self.repo = repo

    async def replace_schedule_assignments(
            self, schedule_id: UUID, items: List[MicroserviceAssignment]
    ) -> None:
        """Replaces all lessons of a schedule (manual edits from the admin table) in one transaction."""
        problems = await self.repo.find_missing_references(items)
        if problems:
            raise ValidationError("; ".join(sorted(problems)[:10]))

        timeslots = await self.repo.get_timeslots({i.timeslot_id for i in items})
        clashes = self._find_clashes(items, timeslots)
        if clashes:
            raise ConflictError("; ".join(clashes[:10]))

        await self.repo.delete_by_schedule_id(schedule_id)
        await self.repo.bulk_create([
            AssignmentCreate(**i.model_dump(), schedule_id=schedule_id) for i in items
        ])

    @staticmethod
    def _find_clashes(items: List[MicroserviceAssignment], timeslots: dict) -> List[str]:
        # An "ALL" slot runs every week, so it overlaps the ODD and EVEN slot of the same day/pair
        by_resource = defaultdict(list)
        for i in items:
            day, lesson, freq = timeslots[i.timeslot_id]
            keys = [("teacher", i.teacher_id), ("group", (i.group_id, i.subgroup_no))]
            if i.room_id is not None:
                keys.append(("room", i.room_id))
            for key in keys:
                by_resource[(key, day, lesson)].append(freq)
        clashes = []
        for ((kind, ident), day, lesson), freqs in by_resource.items():
            all_count = freqs.count("ALL")
            if all_count > 1 or (all_count and len(freqs) > 1) or freqs.count("ODD") > 1 or freqs.count("EVEN") > 1:
                who = ident[0] if kind == "group" else ident
                clashes.append(f"{kind} {who} has overlapping lessons on day {day}, pair {lesson}")
        return clashes

    async def get_schedule_details(self, schedule_id: UUID) -> List[AssignmentDetails]:
        rows = await self.repo.find_by_schedule_id_with_names(schedule_id)
        details = []
        for assignment, last, first, patronymic, group_name, course_name, room_name in rows:
            item = AssignmentDetails.model_validate(assignment)
            item.teacher_name = " ".join(p for p in (last, first, patronymic) if p)
            item.group_name = group_name
            item.course_name = course_name
            item.room_name = room_name
            details.append(item)
        return details

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

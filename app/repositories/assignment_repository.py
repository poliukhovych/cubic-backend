from uuid import UUID
from typing import List, Optional, Union
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.scheduling.assignment import Assignment
from app.schemas.assignment import AssignmentCreate
from app.utils.unset import UNSET


class AssignmentRepository:
    """Repository for managing schedule assignments."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Assignment]:
        """Finds all assignments, ordered by schedule and time."""
        stmt = select(Assignment).order_by(Assignment.schedule_id, Assignment.timeslot_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, assignment_id: UUID) -> Optional[Assignment]:
        """Finds a single assignment by its primary key."""
        stmt = select(Assignment).where(Assignment.assignment_id == assignment_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_schedule_id(self, schedule_id: UUID) -> List[Assignment]:
        """Finds all assignments for a given schedule ID."""
        stmt = (
            select(Assignment)
            .where(Assignment.schedule_id == schedule_id)
            .order_by(Assignment.timeslot_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_schedule_and_group(
            self,
            schedule_id: UUID,
            group_id: UUID
    ) -> List[Assignment]:
        """Finds all assignments for a specific group in a schedule."""
        stmt = (
            select(Assignment)
            .where(
                Assignment.schedule_id == schedule_id,
                Assignment.group_id == group_id
            )
            .order_by(Assignment.timeslot_id, Assignment.subgroup_no)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_schedule_and_teacher(
            self,
            schedule_id: UUID,
            teacher_id: UUID
    ) -> List[Assignment]:
        """Finds all assignments for a specific teacher in a schedule."""
        stmt = (
            select(Assignment)
            .where(
                Assignment.schedule_id == schedule_id,
                Assignment.teacher_id == teacher_id
            )
            .order_by(Assignment.timeslot_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_teacher_id(self, teacher_id: UUID) -> List[Assignment]:
        """Finds all assignments for a teacher across all schedules."""
        stmt = (
            select(Assignment)
            .where(Assignment.teacher_id == teacher_id)
            .order_by(Assignment.schedule_id, Assignment.timeslot_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_group_id(self, group_id: UUID) -> List[Assignment]:
        """Finds all assignments for a group across all schedules."""
        stmt = (
            select(Assignment)
            .where(Assignment.group_id == group_id)
            .order_by(Assignment.schedule_id, Assignment.timeslot_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        schedule_id: UUID,
        timeslot_id: int,
        group_id: UUID,
        subgroup_no: int,
        course_id: UUID,
        teacher_id: UUID,
        room_id: Optional[UUID] = None,
        course_type: str,
    ) -> Assignment:
        """Creates a single assignment record."""
        obj = Assignment(
            schedule_id=schedule_id,
            timeslot_id=timeslot_id,
            group_id=group_id,
            subgroup_no=subgroup_no,
            course_id=course_id,
            teacher_id=teacher_id,
            room_id=room_id,
            course_type=course_type,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    # === METHOD REPLACED ===
    async def bulk_create(
            self,
            assignments: List[AssignmentCreate]
    ) -> List[Assignment]:
        """
        Efficiently bulk-creates assignment records using INSERT ... RETURNING.
        This is compatible with the AssignmentService.
        """
        assignment_dicts = [a.model_dump() for a in assignments]
        if not assignment_dicts:
            return []

        stmt = insert(Assignment).values(assignment_dicts).returning(Assignment)
        result = await self._session.execute(stmt)

        return list(result.scalars().all())

    async def update(
            self,
            assignment_id: UUID,
            *,
            schedule_id: Union[UUID, None, object] = UNSET,
            timeslot_id: Union[int, None, object] = UNSET,
            group_id: Union[UUID, None, object] = UNSET,
            subgroup_no: Union[int, None, object] = UNSET,
            course_id: Union[UUID, None, object] = UNSET,
            teacher_id: Union[UUID, None, object] = UNSET,
            room_id: Union[UUID, None, object] = UNSET,
            course_type: Union[str, None, object] = UNSET,
    ) -> Optional[Assignment]:
        """Updates an existing assignment using the UNSET pattern."""
        update_data = {}
        if schedule_id is not UNSET:
            update_data["schedule_id"] = schedule_id
        if timeslot_id is not UNSET:
            update_data["timeslot_id"] = timeslot_id
        if group_id is not UNSET:
            update_data["group_id"] = group_id
        if subgroup_no is not UNSET:
            update_data["subgroup_no"] = subgroup_no
        if course_id is not UNSET:
            update_data["course_id"] = course_id
        if teacher_id is not UNSET:
            update_data["teacher_id"] = teacher_id
        if room_id is not UNSET:
            update_data["room_id"] = room_id
        if course_type is not UNSET:
            update_data["course_type"] = course_type

        if not update_data:
            return await self.find_by_id(assignment_id)

        stmt = (
            update(Assignment)
            .where(Assignment.assignment_id == assignment_id)
            .values(**update_data)
            .returning(Assignment)
        )
        result = await self._session.execute(stmt)
        updated_assignment = result.scalar_one_or_none()

        if updated_assignment:
            await self._session.refresh(updated_assignment)

        return updated_assignment

    async def delete(self, assignment_id: UUID) -> bool:
        """Deletes a single assignment by its ID."""
        stmt = delete(Assignment).where(Assignment.assignment_id == assignment_id).returning(Assignment.assignment_id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    async def delete_by_schedule_id(self, schedule_id: UUID) -> int:
        """Deletes all assignments for a specific schedule. Returns count of deleted assignments."""
        stmt = delete(Assignment).where(Assignment.schedule_id == schedule_id).returning(Assignment.assignment_id)
        result = await self._session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        return len(deleted_ids)

    async def exists(self, assignment_id: UUID) -> bool:
        """Checks if an assignment exists by its ID."""
        stmt = select(Assignment.assignment_id).where(Assignment.assignment_id == assignment_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

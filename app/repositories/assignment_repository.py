from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.scheduling.assignment import Assignment


class AssignmentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Assignment]:
        stmt = select(Assignment).order_by(Assignment.schedule_id, Assignment.timeslot_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, assignment_id: UUID) -> Optional[Assignment]:
        stmt = select(Assignment).where(Assignment.assignment_id == assignment_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_schedule_id(self, schedule_id: UUID) -> List[Assignment]:
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
        stmt = (
            select(Assignment)
            .where(Assignment.teacher_id == teacher_id)
            .order_by(Assignment.schedule_id, Assignment.timeslot_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_group_id(self, group_id: UUID) -> List[Assignment]:
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

    async def create_bulk(
        self,
        assignments: List[dict]
    ) -> List[Assignment]:
        """Create multiple assignments at once. Useful for saving generated schedules."""
        objs = [
            Assignment(
                schedule_id=a["schedule_id"],
                timeslot_id=a["timeslot_id"],
                group_id=a["group_id"],
                subgroup_no=a["subgroup_no"],
                course_id=a["course_id"],
                teacher_id=a["teacher_id"],
                room_id=a.get("room_id"),
                course_type=a["course_type"],
            )
            for a in assignments
        ]
        self._session.add_all(objs)
        await self._session.flush()
        for obj in objs:
            await self._session.refresh(obj)
        return objs

    async def update(
        self,
        assignment_id: UUID,
        *,
        schedule_id: Optional[UUID] = None,
        timeslot_id: Optional[int] = None,
        group_id: Optional[UUID] = None,
        subgroup_no: Optional[int] = None,
        course_id: Optional[UUID] = None,
        teacher_id: Optional[UUID] = None,
        room_id: Optional[UUID] = None,
        course_type: Optional[str] = None,
    ) -> Optional[Assignment]:
        update_data = {}
        if schedule_id is not None:
            update_data["schedule_id"] = schedule_id
        if timeslot_id is not None:
            update_data["timeslot_id"] = timeslot_id
        if group_id is not None:
            update_data["group_id"] = group_id
        if subgroup_no is not None:
            update_data["subgroup_no"] = subgroup_no
        if course_id is not None:
            update_data["course_id"] = course_id
        if teacher_id is not None:
            update_data["teacher_id"] = teacher_id
        if room_id is not None:
            update_data["room_id"] = room_id
        if course_type is not None:
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
        stmt = delete(Assignment).where(Assignment.assignment_id == assignment_id).returning(Assignment.assignment_id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    async def delete_by_schedule_id(self, schedule_id: UUID) -> int:
        """Delete all assignments for a specific schedule. Returns count of deleted assignments."""
        stmt = delete(Assignment).where(Assignment.schedule_id == schedule_id).returning(Assignment.assignment_id)
        result = await self._session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        return len(deleted_ids)

    async def exists(self, assignment_id: UUID) -> bool:
        stmt = select(Assignment.assignment_id).where(Assignment.assignment_id == assignment_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


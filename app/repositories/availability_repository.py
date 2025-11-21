from sqlalchemy import select, delete, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Dict, Any

from app.db.models.scheduling.teacher_availability import TeacherAvailability
from app.db.models.scheduling.group_availability import GroupUnavailability
from app.db.models.scheduling.teacher_preference import TeacherPreference


class AvailabilityRepository:
    """
    Handles database interactions for availability (teachers/groups) and teacher preferences.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Teacher Availability ---

    async def get_teacher_availability(self, teacher_id: UUID) -> List[int]:
        """
        Retrieves a list of timeslot IDs marked as 'available' for a specific teacher.
        """
        stmt = select(TeacherAvailability.timeslot_id).where(
            TeacherAvailability.teacher_id == teacher_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_teacher_availability(self, teacher_id: UUID, timeslot_ids: List[int]):
        """
        Sets a teacher's availability by replacing all existing entries
        with the new list of timeslot IDs.
        """
        # 1. Clear existing entries for this teacher
        await self.session.execute(
            delete(TeacherAvailability).where(TeacherAvailability.teacher_id == teacher_id)
        )

        if not timeslot_ids:
            return

        # 2. Bulk insert new entries
        values = [{"teacher_id": teacher_id, "timeslot_id": tid} for tid in timeslot_ids]
        await self.session.execute(insert(TeacherAvailability), values)

    # --- Group Availability ---

    async def get_group_unavailability(self, group_id: UUID) -> List[int]:
        """
        Retrieves a list of timeslot IDs marked as 'unavailable' for a specific group.
        """
        stmt = select(GroupUnavailability.timeslot_id).where(
            GroupUnavailability.group_id == group_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Teacher Preferences ---

    async def get_teacher_preferences(self, teacher_id: UUID) -> Dict[str, Any]:
        """
        Retrieves the preference JSON object for a teacher.
        Returns an empty dict if no record exists.
        """
        stmt = select(TeacherPreference.preferences).where(
            TeacherPreference.teacher_id == teacher_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or {}

    async def upsert_teacher_preferences(self, teacher_id: UUID, prefs: Dict[str, Any]):
        """
        Inserts or updates the preference JSON for a teacher.
        Uses PostgreSQL ON CONFLICT DO UPDATE.
        """
        stmt = pg_insert(TeacherPreference).values(
            teacher_id=teacher_id,
            preferences=prefs
        ).on_conflict_do_update(
            index_elements=['teacher_id'],
            set_={"preferences": prefs}
        )
        await self.session.execute(stmt)

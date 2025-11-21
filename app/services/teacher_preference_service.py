from uuid import UUID
from typing import Dict, Any

from app.repositories.availability_repository import AvailabilityRepository


class TeacherPreferenceService:
    """
    Service for managing teacher preferences (JSON).
    """
    def __init__(self, availability_repo: AvailabilityRepository):
        self.repo = availability_repo

    async def get_preferences(self, teacher_id: UUID) -> Dict[str, Any]:
        return await self.repo.get_teacher_preferences(teacher_id)

    async def update_preferences(self, teacher_id: UUID, prefs: Dict[str, Any]):
        await self.repo.upsert_teacher_preferences(teacher_id, prefs)

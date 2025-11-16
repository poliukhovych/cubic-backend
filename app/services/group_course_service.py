from typing import List
from app.repositories.constraint_repository import ConstraintRepository
from app.db.models.joins.group_course import GroupCourse

class GroupCourseService:
    """
    Service for accessing Group-Course links.
    Used to determine which groups take which courses, including frequency.
    """
    def __init__(self, repo: ConstraintRepository):
        self.repo = repo

    async def get_all_links(self) -> List[GroupCourse]:
        return await self.repo.get_group_course_links()

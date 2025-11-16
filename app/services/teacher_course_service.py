from typing import List
from app.repositories.constraint_repository import ConstraintRepository
from app.db.models.joins.teacher_course import TeacherCourse

class TeacherCourseService:
    """
    Service for accessing Teacher-Course links.
    Used to map courses to their assigned teachers.
    """
    def __init__(self, repo: ConstraintRepository):
        self.repo = repo

    async def get_all_links(self) -> List[TeacherCourse]:
        return await self.repo.get_teacher_course_links()

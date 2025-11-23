from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.academic.grade import Grade
from app.db.models.catalog.course import Course


class GradeRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_student_id(self, student_id: UUID) -> List[Grade]:
        """Finds all grades for a specific student."""
        stmt = (
            select(Grade)
            .where(Grade.student_id == student_id)
            .order_by(Grade.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_student_and_course(
        self, student_id: UUID, course_id: UUID
    ) -> List[Grade]:
        """Finds all grades for a specific student and course."""
        stmt = (
            select(Grade)
            .where(
                Grade.student_id == student_id,
                Grade.course_id == course_id
            )
            .order_by(Grade.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, grade_id: UUID) -> Optional[Grade]:
        """Finds a single grade by its ID."""
        stmt = select(Grade).where(Grade.grade_id == grade_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_student_grades_grouped_by_course(
        self, student_id: UUID
    ) -> List[dict]:
        """
        Gets all grades for a student grouped by course with totals.
        Returns a list of dictionaries with course info and grades.
        """
        stmt = (
            select(
                Course.course_id,
                Course.name,
                Grade.grade_id,
                Grade.points,
                Grade.max_points,
                Grade.comment,
                Grade.classroom_url,
                Grade.created_at,
            )
            .join(Course, Course.course_id == Grade.course_id)
            .where(Grade.student_id == student_id)
            .order_by(Course.name, Grade.created_at.desc())
        )
        result = await self._session.execute(stmt)
        rows = result.all()

        # Group by course
        courses_dict = {}
        for row in rows:
            course_id = str(row.course_id)
            if course_id not in courses_dict:
                courses_dict[course_id] = {
                    "course_id": course_id,
                    "course_name": row.name,
                    "grades": [],
                    "total": 0.0,
                }
            
            grade_data = {
                "grade_id": str(row.grade_id),
                "points": float(row.points),
                "max_points": float(row.max_points) if row.max_points else None,
                "comment": row.comment,
                "classroom_url": row.classroom_url,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            courses_dict[course_id]["grades"].append(grade_data)
            courses_dict[course_id]["total"] += float(row.points)

        return list(courses_dict.values())


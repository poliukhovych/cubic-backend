from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.repositories.grade_repository import GradeRepository
from app.db.models.academic.grade import Grade


class GradeService:
    def __init__(self, repo: GradeRepository):
        self.repo = repo

    async def get_student_grades(self, student_id: UUID) -> Dict[str, Any]:
        """
        Gets all grades for a student grouped by course.
        Returns data in the format expected by the frontend.
        """
        grades_by_course = await self.repo.get_student_grades_grouped_by_course(student_id)
        
        subjects = []
        for course_data in grades_by_course:
            grade_items = []
            for grade in course_data["grades"]:
                grade_items.append({
                    "id": grade["grade_id"],
                    "subject": course_data["course_name"],
                    "points": grade["points"],
                    "max": grade["max_points"],
                    "comment": grade["comment"],
                    "createdAt": grade["created_at"],
                    "classroomUrl": grade["classroom_url"],
                })
            
            subjects.append({
                "subject": course_data["course_name"],
                "items": grade_items,
                "total": course_data["total"],
            })
        
        return {
            "studentId": str(student_id),
            "subjects": subjects,
            "updatedAt": datetime.now().isoformat(),
        }


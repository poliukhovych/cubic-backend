from typing import List, Dict, Any
from uuid import UUID
from app.repositories.homework_repository import HomeworkRepository
from app.db.models.academic.homework import Homework, HomeworkFile


class HomeworkService:
    def __init__(self, repo: HomeworkRepository, course_repo=None):
        self.repo = repo
        # course_repo is kept for backward compatibility but not used anymore

    async def get_student_homework(
        self, student_id: UUID, include_done: bool = True
    ) -> Dict[str, Any]:
        """
        Gets all homework for a student.
        Returns data in the format expected by the frontend.
        Uses optimized query with JOIN to get course names.
        """
        # Use optimized method that joins with Course table
        homework_with_courses = await self.repo.find_by_student_id_with_course(
            student_id, include_done
        )
        max_weeks = await self.repo.get_max_weeks_for_student(student_id)
        
        tasks = []
        for hw, course_name in homework_with_courses:
            # Get files for this homework
            files = await self.repo.find_files_by_homework_id(hw.homework_id)
            
            task_data = {
                "id": str(hw.homework_id),
                "subject": course_name,  # Course name from JOIN
                "text": hw.text,
                "createdAt": hw.created_at.isoformat() if hw.created_at else None,
                "dueDate": hw.due_date.isoformat() if hw.due_date else None,
                "groupId": str(hw.group_id),
                "teacherId": str(hw.teacher_id),
                "done": hw.done,
                "classroomUrl": hw.classroom_url,
                "files": [
                    {
                        "id": str(f.file_id),
                        "url": f.url,
                        "title": f.title,
                    }
                    for f in files
                ] if files else [],
            }
            tasks.append(task_data)
        
        return {
            "tasks": tasks,
            "totalWeeks": max_weeks,
        }


from typing import List, Dict, Any
from uuid import UUID
from datetime import date
from app.repositories.homework_repository import HomeworkRepository
from app.repositories.homework_submission_repository import HomeworkSubmissionRepository
from app.db.models.academic.homework import Homework, HomeworkFile
from app.db.models.academic.homework_submission import HomeworkSubmission


class HomeworkService:
    def __init__(self, repo: HomeworkRepository, submission_repo: HomeworkSubmissionRepository | None = None, course_repo=None):
        self.repo = repo
        self.submission_repo = submission_repo
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

    async def create_homework_for_groups(
        self,
        course_id: UUID,
        group_ids: List[UUID],
        teacher_id: UUID,
        text: str,
        due_date: date,
        classroom_url: str | None = None,
        attachments: List[Dict[str, str]] | None = None,
    ) -> List[Homework]:
        """
        Creates homework assignments for all students in the given groups.
        Returns list of created homework assignments.
        """
        # Get all students in the groups
        students = await self.repo.find_students_by_group_ids(group_ids)
        
        if not students:
            return []
        
        # Create homework for each student
        created_homework = []
        for student in students:
            homework = await self.repo.create(
                student_id=student.student_id,
                course_id=course_id,
                group_id=student.group_id,
                teacher_id=teacher_id,
                text=text,
                due_date=due_date,
                classroom_url=classroom_url,
            )
            created_homework.append(homework)
            
            # Create files if provided
            if attachments:
                for attachment in attachments:
                    await self.repo.create_file(
                        homework_id=homework.homework_id,
                        url=attachment.get("url", ""),
                        title=attachment.get("title"),
                    )
        
        return created_homework

    async def get_teacher_homework(
        self, teacher_id: UUID
    ) -> Dict[str, Any]:
        """
        Gets all homework for a teacher.
        Returns data in the format expected by the frontend.
        """
        homework_with_courses = await self.repo.find_by_teacher_id(teacher_id)
        
        tasks = []
        for hw, course_name in homework_with_courses:
            # Get files for this homework
            files = await self.repo.find_files_by_homework_id(hw.homework_id)
            
            task_data = {
                "id": str(hw.homework_id),
                "subject": course_name,
                "text": hw.text,
                "createdAt": hw.created_at.isoformat() if hw.created_at else None,
                "dueDate": hw.due_date.isoformat() if hw.due_date else None,
                "groupId": str(hw.group_id),
                "teacherId": str(hw.teacher_id),
                "studentId": str(hw.student_id),
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
        }

    async def submit_homework(
        self,
        homework_id: UUID,
        student_id: UUID,
        content: str,
        attachments: List[Dict[str, str]] | None = None,
    ) -> HomeworkSubmission:
        """
        Submits homework by a student.
        Returns the created submission.
        """
        if not self.submission_repo:
            raise ValueError("Submission repository not initialized")
        
        # Check if submission already exists
        existing = await self.submission_repo.find_by_student_and_homework(student_id, homework_id)
        if existing:
            raise ValueError("Homework already submitted")
        
        # Create submission
        submission = await self.submission_repo.create(
            homework_id=homework_id,
            student_id=student_id,
            content=content,
        )
        
        # Create files if provided
        if attachments:
            for attachment in attachments:
                await self.submission_repo.create_file(
                    submission_id=submission.submission_id,
                    url=attachment.get("url", ""),
                    title=attachment.get("title"),
                )
        
        return submission

    async def get_homework_submissions(
        self, homework_id: UUID
    ) -> Dict[str, Any]:
        """
        Gets all submissions for a homework assignment.
        Returns data in the format expected by the frontend.
        """
        if not self.submission_repo:
            raise ValueError("Submission repository not initialized")
        
        submissions = await self.submission_repo.find_by_homework_id(homework_id)
        
        submission_list = []
        for submission in submissions:
            # Get files for this submission
            files = await self.submission_repo.find_files_by_submission_id(submission.submission_id)
            
            submission_data = {
                "id": str(submission.submission_id),
                "homeworkId": str(submission.homework_id),
                "studentId": str(submission.student_id),
                "content": submission.content,
                "submittedAt": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "grade": float(submission.grade) if submission.grade else None,
                "feedback": submission.feedback,
                "files": [
                    {
                        "id": str(f.file_id),
                        "url": f.url,
                        "title": f.title,
                    }
                    for f in files
                ] if files else [],
            }
            submission_list.append(submission_data)
        
        return {
            "submissions": submission_list,
        }


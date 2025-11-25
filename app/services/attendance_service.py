from typing import List, Dict, Any
from uuid import UUID
from datetime import date
from app.repositories.attendance_repository import AttendanceRepository
from app.db.models.academic.attendance import Attendance, AttendanceStatus
from app.db.models.scheduling.assignment import Assignment
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AttendanceService:
    def __init__(self, repo: AttendanceRepository, session: AsyncSession):
        self.repo = repo
        self._session = session

    async def mark_attendance(
        self,
        assignment_id: UUID,
        attendance_date: date,
        students: List[Dict[str, Any]],
    ) -> List[Attendance]:
        """
        Marks attendance for multiple students for a specific assignment.
        students: List of dicts with 'student_id', 'status', and optional 'note'
        """
        # Verify assignment exists
        stmt = select(Assignment).where(Assignment.assignment_id == assignment_id)
        result = await self._session.execute(stmt)
        assignment = result.scalar_one_or_none()
        if not assignment:
            raise ValueError(f"Assignment with id {assignment_id} not found")
        
        # Create or update attendance records
        attendance_records = []
        for student_data in students:
            student_id = UUID(student_data["student_id"])
            status = AttendanceStatus(student_data["status"])
            note = student_data.get("note")
            
            attendance = await self.repo.update_or_create(
                assignment_id=assignment_id,
                student_id=student_id,
                date=attendance_date,
                status=status,
                note=note,
            )
            attendance_records.append(attendance)
        
        return attendance_records

    async def get_student_attendance(
        self,
        student_id: UUID,
        course_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Gets attendance records for a student.
        Returns list of attendance records with assignment and course info.
        """
        attendances = await self.repo.find_by_student_id(
            student_id, course_id, from_date, to_date
        )
        
        # TODO: Join with Assignment and Course to get more details
        # For now, return basic info
        return [
            {
                "id": str(att.attendance_id),
                "assignmentId": str(att.assignment_id),
                "studentId": str(att.student_id),
                "date": att.date.isoformat() if att.date else None,
                "status": att.status.value,
                "note": att.note,
                "createdAt": att.created_at.isoformat() if att.created_at else None,
            }
            for att in attendances
        ]


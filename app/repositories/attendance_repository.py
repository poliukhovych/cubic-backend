from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.academic.attendance import Attendance, AttendanceStatus


class AttendanceRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_student_id(
        self, student_id: UUID, course_id: UUID | None = None, from_date: date | None = None, to_date: date | None = None
    ) -> List[Attendance]:
        """Finds all attendance records for a specific student."""
        conditions = [Attendance.student_id == student_id]
        
        if from_date:
            conditions.append(Attendance.date >= from_date)
        if to_date:
            conditions.append(Attendance.date <= to_date)
        
        stmt = (
            select(Attendance)
            .where(and_(*conditions))
            .order_by(Attendance.date.desc(), Attendance.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_assignment_id(self, assignment_id: UUID, attendance_date: date) -> List[Attendance]:
        """Finds all attendance records for a specific assignment on a specific date."""
        stmt = (
            select(Attendance)
            .where(
                Attendance.assignment_id == assignment_id,
                Attendance.date == attendance_date
            )
            .order_by(Attendance.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, attendance_id: UUID) -> Optional[Attendance]:
        """Finds a single attendance record by its ID."""
        stmt = select(Attendance).where(Attendance.attendance_id == attendance_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        assignment_id: UUID,
        student_id: UUID,
        date: date,
        status: AttendanceStatus,
        note: str | None = None,
    ) -> Attendance:
        """Creates a new attendance record."""
        attendance = Attendance(
            assignment_id=assignment_id,
            student_id=student_id,
            date=date,
            status=status,
            note=note,
        )
        self._session.add(attendance)
        await self._session.flush()
        await self._session.refresh(attendance)
        return attendance

    async def create_bulk(
        self,
        attendance_records: List[dict]
    ) -> List[Attendance]:
        """Creates multiple attendance records."""
        attendances = []
        for record in attendance_records:
            attendance = Attendance(
                assignment_id=record["assignment_id"],
                student_id=record["student_id"],
                date=record["date"],
                status=record["status"],
                note=record.get("note"),
            )
            attendances.append(attendance)
        
        self._session.add_all(attendances)
        await self._session.flush()
        for attendance in attendances:
            await self._session.refresh(attendance)
        return attendances

    async def update_or_create(
        self,
        *,
        assignment_id: UUID,
        student_id: UUID,
        date: date,
        status: AttendanceStatus,
        note: str | None = None,
    ) -> Attendance:
        """Updates existing attendance record or creates a new one."""
        stmt = (
            select(Attendance)
            .where(
                Attendance.assignment_id == assignment_id,
                Attendance.student_id == student_id,
                Attendance.date == date
            )
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.status = status
            existing.note = note
            await self._session.flush()
            await self._session.refresh(existing)
            return existing
        else:
            return await self.create(
                assignment_id=assignment_id,
                student_id=student_id,
                date=date,
                status=status,
                note=note,
            )


from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.academic.homework import Homework, HomeworkFile
from app.db.models.catalog.course import Course
from app.db.models.people.student import Student


class HomeworkRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_student_id(
        self, student_id: UUID, include_done: bool = True
    ) -> List[Homework]:
        """Finds all homework for a specific student."""
        conditions = [Homework.student_id == student_id]
        if not include_done:
            conditions.append(Homework.done == False)
        
        stmt = (
            select(Homework)
            .where(and_(*conditions))
            .order_by(Homework.due_date.asc(), Homework.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_student_and_course(
        self, student_id: UUID, course_id: UUID, include_done: bool = True
    ) -> List[Homework]:
        """Finds all homework for a specific student and course."""
        conditions = [
            Homework.student_id == student_id,
            Homework.course_id == course_id
        ]
        if not include_done:
            conditions.append(Homework.done == False)
        
        stmt = (
            select(Homework)
            .where(and_(*conditions))
            .order_by(Homework.due_date.asc(), Homework.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, homework_id: UUID) -> Optional[Homework]:
        """Finds a single homework by its ID."""
        stmt = select(Homework).where(Homework.homework_id == homework_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_files_by_homework_id(self, homework_id: UUID) -> List[HomeworkFile]:
        """Finds all files for a specific homework."""
        stmt = (
            select(HomeworkFile)
            .where(HomeworkFile.homework_id == homework_id)
            .order_by(HomeworkFile.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_student_id_with_course(
        self, student_id: UUID, include_done: bool = True
    ) -> List[tuple]:
        """
        Finds all homework for a specific student with course names joined.
        Returns list of tuples: (Homework, Course.name)
        """
        conditions = [Homework.student_id == student_id]
        if not include_done:
            conditions.append(Homework.done == False)
        
        stmt = (
            select(Homework, Course.name)
            .join(Course, Course.course_id == Homework.course_id)
            .where(and_(*conditions))
            .order_by(Homework.due_date.asc(), Homework.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.all())

    async def get_max_weeks_for_student(self, student_id: UUID) -> int:
        """
        Calculates the maximum number of weeks between the earliest and latest homework
        due dates for a student. Returns 0 if no homework exists.
        """
        stmt = (
            select(
                func.min(Homework.due_date).label("min_date"),
                func.max(Homework.due_date).label("max_date")
            )
            .where(Homework.student_id == student_id)
        )
        result = await self._session.execute(stmt)
        row = result.one_or_none()
        
        if not row or not row.min_date or not row.max_date:
            return 0
        
        delta = row.max_date - row.min_date
        weeks = (delta.days // 7) + 1  # At least 1 week
        return max(weeks, 1)

    async def create(
        self,
        *,
        student_id: UUID,
        course_id: UUID,
        group_id: UUID,
        teacher_id: UUID,
        text: str,
        due_date: date,
        classroom_url: str | None = None,
    ) -> Homework:
        """Creates a new homework assignment."""
        homework = Homework(
            student_id=student_id,
            course_id=course_id,
            group_id=group_id,
            teacher_id=teacher_id,
            text=text,
            due_date=due_date,
            classroom_url=classroom_url,
        )
        self._session.add(homework)
        await self._session.flush()
        await self._session.refresh(homework)
        return homework

    async def create_file(
        self,
        *,
        homework_id: UUID,
        url: str,
        title: str | None = None,
    ) -> HomeworkFile:
        """Creates a new homework file."""
        file = HomeworkFile(
            homework_id=homework_id,
            url=url,
            title=title,
        )
        self._session.add(file)
        await self._session.flush()
        await self._session.refresh(file)
        return file

    async def find_by_teacher_id(
        self, teacher_id: UUID
    ) -> List[tuple]:
        """
        Finds all homework for a specific teacher with course names joined.
        Returns list of tuples: (Homework, Course.name)
        """
        stmt = (
            select(Homework, Course.name)
            .join(Course, Course.course_id == Homework.course_id)
            .where(Homework.teacher_id == teacher_id)
            .order_by(Homework.due_date.desc(), Homework.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.all())

    async def find_students_by_group_ids(self, group_ids: List[UUID]) -> List[Student]:
        """Finds all students in the given groups."""
        stmt = (
            select(Student)
            .where(Student.group_id.in_(group_ids))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


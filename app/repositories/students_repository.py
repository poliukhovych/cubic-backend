from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.people.student import Student
from app.db.models.joins.student_group import StudentGroup


class StudentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Student]:
        stmt = select(Student).order_by(Student.last_name, Student.first_name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, student_id: UUID) -> Optional[Student]:
        stmt = select(Student).where(Student.student_id == student_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_user_id(self, user_id: UUID) -> Optional[Student]:
        stmt = select(Student).where(Student.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_group_id(self, group_id: UUID) -> List[Student]:
        stmt = (
            select(Student)
            .join(StudentGroup, StudentGroup.student_id == Student.student_id)
            .where(StudentGroup.group_id == group_id)
            .order_by(Student.last_name, Student.first_name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, student_id: UUID) -> Optional[Student]:
        """Legacy method, use find_by_id instead."""
        return await self.find_by_id(student_id)

    async def create(
            self,
            *,
            first_name: str,
            last_name: str,
            patronymic: str | None = None,
            status: str = "pending",
            user_id: Optional[UUID] = None,
            group_id: Optional[UUID] = None,
    ) -> Student:
        obj = Student(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            status=status,
            user_id=user_id,
            group_id=group_id,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(
            self,
            student_id: UUID,
            *,
            first_name: str | None = None,
            last_name: str | None = None,
            patronymic: str | None = None,
            status: str | None = None,
            user_id: Optional[UUID] = None,
            group_id: Optional[UUID] = None,
    ) -> Optional[Student]:
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if patronymic is not None:
            update_data["patronymic"] = patronymic
        if status is not None:
            update_data["status"] = status
        if user_id is not None:
            update_data["user_id"] = user_id
        if group_id is not None:
            update_data["group_id"] = group_id

        if not update_data:
            return await self.find_by_id(student_id)

        stmt = (
            update(Student)
            .where(Student.student_id == student_id)
            .values(**update_data)
            .returning(Student)
        )

        res = await self._session.execute(stmt)
        obj = res.scalar_one_or_none()

        if obj is None:
            return None

        await self._session.refresh(obj)
        return obj

    async def delete(self, student_id: UUID) -> bool:
        stmt = (
            delete(Student)
            .where(Student.student_id == student_id)
            .returning(Student.student_id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def activate_student(self, student_id: UUID) -> Optional[Student]:
        return await self.update(student_id, status="active")

    async def deactivate_student(self, student_id: UUID) -> Optional[Student]:
        return await self.update(student_id, status="inactive")

    async def exists(self, student_id: UUID) -> bool:
        stmt = select(Student.student_id).where(Student.student_id == student_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

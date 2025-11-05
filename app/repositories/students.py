from uuid import UUID
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.people.student import Student


class StudentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
            self,
            *,
            first_name: str,
            last_name: str,
            patronymic: str | None = None,
            confirmed: bool = False,
    ) -> Student:
        obj = Student(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            confirmed=confirmed,
        )
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def get(self, student_id: UUID) -> Student | None:
        return await self._session.get(Student, student_id)

    async def update(
            self,
            student_id: UUID,
            *,
            first_name: str | None = None,
            last_name: str | None = None,
            patronymic: str | None = None,
            confirmed: bool | None = None,
    ) -> Student | None:
        stmt = (
            update(Student)
            .where(Student.student_id == student_id)
            .values(
                **{
                    k: v for k, v in dict(
                        first_name=first_name,
                        last_name=last_name,
                        patronymic=patronymic,
                        confirmed=confirmed,
                    ).items() if v is not None
                }
            )
            .returning(Student)
        )

        res = await self._session.execute(stmt)
        obj = res.scalar_one_or_none()

        if obj is None:
            return None

        return obj

    async def delete(self, student_id: UUID) -> bool:
        stmt = (
            delete(Student)
            .where(Student.student_id == student_id)
            .returning(Student.student_id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none() is not None

from uuid import UUID
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.student import Student


class StudentRepository:
    async def create(
            self,
            session: AsyncSession,
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
        session.add(obj)
        await session.flush()
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get(self, session: AsyncSession, student_id: UUID) -> Student | None:
        return await session.get(Student, student_id)

    async def update(
            self,
            session: AsyncSession,
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

        res = await session.execute(stmt)
        obj = res.scalar_one_or_none()

        if obj is None:
            await session.rollback()
            return None

        await session.commit()
        return obj

    # DELETE
    async def delete(self, session: AsyncSession, student_id: UUID) -> bool:
        stmt = (
            delete(Student)
            .where(Student.student_id == student_id)
            .returning(Student.student_id)
        )
        res = await session.execute(stmt)
        await session.commit()
        return res.scalar_one_or_none() is not None

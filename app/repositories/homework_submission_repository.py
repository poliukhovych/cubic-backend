from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.academic.homework_submission import HomeworkSubmission, HomeworkSubmissionFile


class HomeworkSubmissionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_homework_id(self, homework_id: UUID) -> List[HomeworkSubmission]:
        """Finds all submissions for a specific homework."""
        stmt = (
            select(HomeworkSubmission)
            .where(HomeworkSubmission.homework_id == homework_id)
            .order_by(HomeworkSubmission.submitted_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_student_and_homework(
        self, student_id: UUID, homework_id: UUID
    ) -> Optional[HomeworkSubmission]:
        """Finds a submission by student and homework."""
        stmt = (
            select(HomeworkSubmission)
            .where(
                HomeworkSubmission.student_id == student_id,
                HomeworkSubmission.homework_id == homework_id
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, submission_id: UUID) -> Optional[HomeworkSubmission]:
        """Finds a single submission by its ID."""
        stmt = select(HomeworkSubmission).where(HomeworkSubmission.submission_id == submission_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        homework_id: UUID,
        student_id: UUID,
        content: str,
    ) -> HomeworkSubmission:
        """Creates a new homework submission."""
        submission = HomeworkSubmission(
            homework_id=homework_id,
            student_id=student_id,
            content=content,
        )
        self._session.add(submission)
        await self._session.flush()
        await self._session.refresh(submission)
        return submission

    async def create_file(
        self,
        *,
        submission_id: UUID,
        url: str,
        title: str | None = None,
    ) -> HomeworkSubmissionFile:
        """Creates a new submission file."""
        file = HomeworkSubmissionFile(
            submission_id=submission_id,
            url=url,
            title=title,
        )
        self._session.add(file)
        await self._session.flush()
        await self._session.refresh(file)
        return file

    async def find_files_by_submission_id(self, submission_id: UUID) -> List[HomeworkSubmissionFile]:
        """Finds all files for a specific submission."""
        stmt = (
            select(HomeworkSubmissionFile)
            .where(HomeworkSubmissionFile.submission_id == submission_id)
            .order_by(HomeworkSubmissionFile.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


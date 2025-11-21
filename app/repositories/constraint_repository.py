from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.db.models.joins.group_course import GroupCourse
from app.db.models.joins.teacher_course import TeacherCourse
from app.db.models.scheduling.subgroup_constraints import SubgroupConstraints

class ConstraintRepository:
    """
    Handles retrieval of constraint and linkage data required for
    constructing the schedule problem instance.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_group_course_links(self) -> List[GroupCourse]:
        """
        Retrieves all GroupCourse links, including scheduling columns.
        """
        stmt = select(GroupCourse)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_teacher_course_links(self) -> List[TeacherCourse]:
        """
        Retrieves all TeacherCourse links to map courses to teachers.
        """
        stmt = select(TeacherCourse)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_subgroup_constraints(self, schedule_id: UUID) -> List[SubgroupConstraints]:
        """
        Retrieves subgroup constraints for a specific schedule context.
        """
        stmt = select(SubgroupConstraints).where(
            SubgroupConstraints.schedule_id == schedule_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

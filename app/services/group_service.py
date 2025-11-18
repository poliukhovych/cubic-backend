from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.group_repository import GroupRepository
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse, GroupListResponse
from app.db.models.catalog.group import Group
from app.utils.unset import UNSET


class GroupService:
    def __init__(self, repo: GroupRepository):
        self.repo = repo

    async def get_all_groups(self) -> GroupListResponse:
        groups = await self.repo.find_all()
        total = await self.repo.count()
        
        return GroupListResponse(
            groups=[GroupResponse.model_validate(group) for group in groups],
            total=total
        )

    async def get_group_by_id(self, group_id: UUID) -> Optional[GroupResponse]:
        group = await self.repo.find_by_id(group_id)
        if not group:
            return None
        return GroupResponse.model_validate(group)

    async def get_groups_by_teacher_id(self, teacher_id: UUID) -> List[GroupResponse]:
        groups = await self.repo.find_by_teacher_id(teacher_id)
        return [GroupResponse.model_validate(group) for group in groups]

    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        existing_group = await self.repo.find_by_name(group_data.name)
        if existing_group:
            raise ValueError(f"Group: '{group_data.name}' already exist")
        
        # Validate course range based on type
        if group_data.type == "bachelor" and not (1 <= group_data.course <= 4):
            raise ValueError("Bachelor course must be between 1 and 4")
        if group_data.type == "master" and not (1 <= group_data.course <= 2):
            raise ValueError("Master course must be between 1 and 2")
        
        group = await self.repo.create(
            name=group_data.name,
            size=group_data.size,
            type=group_data.type,
            course=group_data.course
        )
        return GroupResponse.model_validate(group)

    async def update_group(self, group_id: UUID, group_data: GroupUpdate) -> Optional[GroupResponse]:
        existing_group = await self.repo.find_by_id(group_id)
        if not existing_group:
            return None
        
        if group_data.name is not UNSET and group_data.name is not None and group_data.name != existing_group.name:
            name_conflict = await self.repo.find_by_name(group_data.name)
            if name_conflict:
                raise ValueError(f"Group: '{group_data.name}' already exist")
        
        # Validate course range based on type (use existing type if not updating)
        final_type = group_data.type if group_data.type is not UNSET else existing_group.type
        final_course = group_data.course if group_data.course is not UNSET else existing_group.course
        
        if final_type == "bachelor" and not (1 <= final_course <= 4):
            raise ValueError("Bachelor course must be between 1 and 4")
        if final_type == "master" and not (1 <= final_course <= 2):
            raise ValueError("Master course must be between 1 and 2")
        
        updated_group = await self.repo.update(
            group_id=group_id,
            name=group_data.name,
            size=group_data.size,
            type=group_data.type,
            course=group_data.course
        )
        
        if not updated_group:
            return None
        
        return GroupResponse.model_validate(updated_group)

    async def delete_group(self, group_id: UUID) -> bool:
        result = await self.repo.delete(group_id)
        return result

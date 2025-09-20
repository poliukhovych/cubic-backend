from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.group_repository import GroupRepository
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse, GroupListResponse
from app.db.models.catalog.group import Group


class GroupService:
    def __init__(self, session: AsyncSession):
        self._repository = GroupRepository(session)

    async def get_all_groups(self) -> GroupListResponse:
        """Отримати всі групи"""
        groups = await self._repository.find_all()
        total = await self._repository.count()
        
        return GroupListResponse(
            groups=[GroupResponse.model_validate(group) for group in groups],
            total=total
        )

    async def get_group_by_id(self, group_id: UUID) -> Optional[GroupResponse]:
        """Отримати групу за ID"""
        group = await self._repository.find_by_id(group_id)
        if not group:
            return None
        return GroupResponse.model_validate(group)

    async def get_groups_by_teacher_id(self, teacher_id: UUID) -> List[GroupResponse]:
        """Отримати групи за ID викладача"""
        groups = await self._repository.find_by_teacher_id(teacher_id)
        return [GroupResponse.model_validate(group) for group in groups]

    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        """Створити нову групу"""
        # Перевірити, чи не існує група з такою назвою
        existing_group = await self._repository.find_by_name(group_data.name)
        if existing_group:
            raise ValueError(f"Група з назвою '{group_data.name}' вже існує")
        
        group = await self._repository.create(
            name=group_data.name,
            size=group_data.size
        )
        await self._repository._session.commit()
        return GroupResponse.model_validate(group)

    async def update_group(self, group_id: UUID, group_data: GroupUpdate) -> Optional[GroupResponse]:
        """Оновити групу"""
        # Перевірити, чи існує група
        existing_group = await self._repository.find_by_id(group_id)
        if not existing_group:
            return None
        
        # Перевірити, чи не існує інша група з такою назвою (якщо назва змінюється)
        if group_data.name and group_data.name != existing_group.name:
            name_conflict = await self._repository.find_by_name(group_data.name)
            if name_conflict:
                raise ValueError(f"Група з назвою '{group_data.name}' вже існує")
        
        updated_group = await self._repository.update(
            group_id=group_id,
            name=group_data.name,
            size=group_data.size
        )
        
        if not updated_group:
            return None
        
        await self._repository._session.commit()
        return GroupResponse.model_validate(updated_group)

    async def delete_group(self, group_id: UUID) -> bool:
        """Видалити групу"""
        result = await self._repository.delete(group_id)
        if result:
            await self._repository._session.commit()
        return result

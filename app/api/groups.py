from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID

from app.services.group_service import GroupService
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse, GroupListResponse
from app.core.deps import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


async def get_group_service(session: AsyncSession = Depends(get_session)) -> GroupService:
    """Dependency для отримання GroupService з сесією БД"""
    return GroupService(session)


@router.get("/", response_model=GroupListResponse)
async def get_all_groups(
    group_service: GroupService = Depends(get_group_service)
) -> GroupListResponse:
    """Отримати всі групи"""
    return await group_service.get_all_groups()


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group_by_id(
    group_id: UUID,
    group_service: GroupService = Depends(get_group_service)
) -> GroupResponse:
    """Отримати групу за ID"""
    group = await group_service.get_group_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Групу не знайдено")
    return group


@router.get("/by-teacher/{teacher_id}", response_model=List[GroupResponse])
async def get_groups_by_teacher_id(
    teacher_id: UUID,
    group_service: GroupService = Depends(get_group_service)
) -> List[GroupResponse]:
    """Отримати групи за ID викладача"""
    return await group_service.get_groups_by_teacher_id(teacher_id)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_group(
    group_data: GroupCreate,
    group_service: GroupService = Depends(get_group_service)
) -> GroupResponse:
    """Створити нову групу"""
    try:
        return await group_service.create_group(group_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: UUID,
    group_data: GroupUpdate,
    group_service: GroupService = Depends(get_group_service)
) -> GroupResponse:
    """Оновити групу"""
    try:
        updated_group = await group_service.update_group(group_id, group_data)
        if not updated_group:
            raise HTTPException(status_code=404, detail="Групу не знайдено")
        return updated_group
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{group_id}")
async def delete_group(
    group_id: UUID,
    group_service: GroupService = Depends(get_group_service)
) -> dict[str, str]:
    """Видалити групу"""
    success = await group_service.delete_group(group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Групу не знайдено")
    return {"message": "Групу успішно видалено"}

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.group_service import GroupService
from app.core.deps import get_group_service

router = APIRouter()


@router.get("/")
async def get_all_groups(
    group_service: GroupService = Depends(get_group_service)
) -> List[Dict[str, Any]]:
    groups = await group_service.get_all_groups()
    return groups


@router.get("/{group_id}")
async def get_group_by_id(
    group_id: str,
    group_service: GroupService = Depends(get_group_service)
) -> Dict[str, Any]:
    group = await group_service.get_group_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.get("/by-teacher/{teacher_id}")
async def get_groups_by_teacher_id(
    teacher_id: str,
    group_service: GroupService = Depends(get_group_service)
) -> List[Dict[str, Any]]:
    groups = await group_service.get_groups_by_teacher_id(teacher_id)
    return groups


@router.post("/")
async def create_group(
    group_data: Dict[str, Any],
    group_service: GroupService = Depends(get_group_service)
) -> Dict[str, Any]:
    new_group = await group_service.create_group(group_data)
    return new_group


@router.delete("/{group_id}")
async def delete_group(
    group_id: str,
    group_service: GroupService = Depends(get_group_service)
) -> Dict[str, str]:
    success = await group_service.delete_group(group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"message": "Group was deleted successfully"}

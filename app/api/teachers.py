from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import uuid

from app.services.teacher_service import TeacherService
from app.services.course_service import CourseService
from app.services.group_service import GroupService
from app.core.deps import get_teacher_service, get_course_service, get_group_service
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse, TeacherListResponse

router = APIRouter()


@router.get("/", response_model=TeacherListResponse)
async def get_all_teachers(
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherListResponse:
    teachers = await teacher_service.get_all_teachers()
    return TeacherListResponse(teachers=teachers, total=len(teachers))


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher_by_id(
    teacher_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with id {teacher_id} not found"
        )
    return teacher


@router.get("/user/{user_id}", response_model=TeacherResponse)
async def get_teacher_by_user_id(
    user_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    teacher = await teacher_service.get_teacher_by_user_id(user_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with user_id {user_id} not found"
        )
    return teacher


@router.get("/{teacher_id}/courses")
async def get_teacher_courses(
    teacher_id: uuid.UUID,
    course_service: CourseService = Depends(get_course_service)
) -> List[dict]:
    # TODO: Implement when course service is ready
    return []


@router.get("/{teacher_id}/groups")
async def get_teacher_groups(
    teacher_id: uuid.UUID,
    group_service: GroupService = Depends(get_group_service)
) -> List[dict]:
    # TODO: Implement when group service is ready
    return []


@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher_data: TeacherCreate,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    try:
        new_teacher = await teacher_service.create_teacher(teacher_data)
        return new_teacher
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create teacher: {str(e)}"
        )


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: uuid.UUID,
    teacher_data: TeacherUpdate,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    teacher = await teacher_service.update_teacher(teacher_id, teacher_data)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with id {teacher_id} not found"
        )
    return teacher


@router.patch("/{teacher_id}/confirm", response_model=TeacherResponse)
async def confirm_teacher(
    teacher_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> TeacherResponse:
    teacher = await teacher_service.confirm_teacher(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with id {teacher_id} not found"
        )
    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: uuid.UUID,
    teacher_service: TeacherService = Depends(get_teacher_service)
):
    success = await teacher_service.delete_teacher(teacher_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Teacher with id {teacher_id} not found"
        )
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.teacher_service import TeacherService
from app.services.course_service import CourseService
from app.services.group_service import GroupService

router = APIRouter()


def get_teacher_service() -> TeacherService:
    return TeacherService()


def get_course_service() -> CourseService:
    return CourseService()


def get_group_service() -> GroupService:
    return GroupService()


@router.get("/")
async def get_all_teachers(
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> List[Dict[str, Any]]:
    teachers = await teacher_service.get_all_teachers()
    return teachers


@router.get("/{teacher_id}")
async def get_teacher_by_id(
    teacher_id: str,
    teacher_service: TeacherService = Depends(get_teacher_service)
) -> Dict[str, Any]:
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Викладач не знайдений")
    return teacher


@router.get("/{teacher_id}/courses")
async def get_teacher_courses(
    teacher_id: str,
    course_service: CourseService = Depends(get_course_service)
) -> List[Dict[str, Any]]:
    courses = await course_service.get_courses_by_teacher_id(teacher_id)
    return courses


@router.get("/{teacher_id}/groups")
async def get_teacher_groups(
    teacher_id: str,
    group_service: GroupService = Depends(get_group_service)
) -> List[Dict[str, Any]]:
    groups = await group_service.get_groups_by_teacher_id(teacher_id)
    return groups

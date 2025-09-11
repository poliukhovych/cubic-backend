from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.course_service import CourseService

router = APIRouter()


def get_course_service() -> CourseService:
    return CourseService()


@router.get("/")
async def get_all_courses(
    course_service: CourseService = Depends(get_course_service)
) -> List[Dict[str, Any]]:
    courses = await course_service.get_all_courses()
    return courses


@router.get("/{course_id}")
async def get_course_by_id(
    course_id: str,
    course_service: CourseService = Depends(get_course_service)
) -> Dict[str, Any]:
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Курс не знайдений")
    return course


@router.get("/by-teacher/{teacher_id}")
async def get_courses_by_teacher_id(
    teacher_id: str,
    course_service: CourseService = Depends(get_course_service)
) -> List[Dict[str, Any]]:
    courses = await course_service.get_courses_by_teacher_id(teacher_id)
    return courses

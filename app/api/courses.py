from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
# from app.services.course_service import CourseService
# from app.core.deps import get_course_service

router = APIRouter()


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
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/by-teacher/{teacher_id}")
async def get_courses_by_teacher_id(
    teacher_id: str,
    course_service: CourseService = Depends(get_course_service)
) -> List[Dict[str, Any]]:
    courses = await course_service.get_courses_by_teacher_id(teacher_id)
    return courses


@router.post("/")
async def create_course(
    course_data: Dict[str, Any],
    course_service: CourseService = Depends(get_course_service)
) -> Dict[str, Any]:
    new_course = await course_service.create_course(course_data)
    return new_course


@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    course_service: CourseService = Depends(get_course_service)
) -> Dict[str, str]:
    success = await course_service.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course was deleted successfully"}

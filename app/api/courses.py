from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from app.services.course_service import CourseService
from app.core.deps import get_course_service
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseListResponse

router = APIRouter()


@router.get("/", response_model=CourseListResponse)
async def get_all_courses(
    course_service: CourseService = Depends(get_course_service)
) -> CourseListResponse:
    return await course_service.get_all_courses()


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_by_id(
    course_id: UUID,
    course_service: CourseService = Depends(get_course_service)
) -> CourseResponse:
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/by-teacher/{teacher_id}", response_model=List[CourseResponse])
async def get_courses_by_teacher_id(
    teacher_id: UUID,
    course_service: CourseService = Depends(get_course_service)
) -> List[CourseResponse]:
    courses = await course_service.get_courses_by_teacher_id(teacher_id)
    return courses


@router.post("/", response_model=CourseResponse, status_code=201)
async def create_course(
    course_data: CourseCreate,
    course_service: CourseService = Depends(get_course_service)
) -> CourseResponse:
    try:
        new_course = await course_service.create_course(course_data)
        return new_course
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    course_service: CourseService = Depends(get_course_service)
) -> CourseResponse:
    """Оновити курс"""
    try:
        updated_course = await course_service.update_course(course_id, course_data)
        if not updated_course:
            raise HTTPException(status_code=404, detail="Course not found")
        return updated_course
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{course_id}")
async def delete_course(
    course_id: UUID,
    course_service: CourseService = Depends(get_course_service)
) -> dict:
    success = await course_service.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="КCourse not found")
    return {"message": "Course was successfully deleted"}
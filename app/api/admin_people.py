from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.people.student import Student
from app.db.models.people.teacher import Teacher
from app.db.models.people.user import User
from app.db.models.catalog.course import Course
from app.schemas.admin import (
    AdminStats,
    AdminStudent, AdminStudentListResponse,
    AdminTeacher, AdminTeacherListResponse,
)
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut
from app.repositories.students_repository import StudentRepository
from app.utils.unset import UNSET
import uuid

router = APIRouter(prefix="/admin", tags=["Admin People"])


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    students_total = await db.execute(select(func.count()).select_from(Student))
    students_confirmed = await db.execute(select(func.count()).select_from(Student).where(Student.confirmed == True))
    teachers_total = await db.execute(select(func.count()).select_from(Teacher))
    teachers_confirmed = await db.execute(select(func.count()).select_from(Teacher).where(Teacher.confirmed == True))
    courses_total = await db.execute(select(func.count()).select_from(Course))

    return AdminStats(
        students_total=students_total.scalar_one(),
        students_confirmed=students_confirmed.scalar_one(),
        teachers_total=teachers_total.scalar_one(),
        teachers_confirmed=teachers_confirmed.scalar_one(),
        courses_total=courses_total.scalar_one(),
    )


@router.get("/students", response_model=AdminStudentListResponse)
async def list_students(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    # total count
    total_res = await db.execute(select(func.count()).select_from(Student))
    total = total_res.scalar_one()

    # left join user to get email if present
    user_alias = aliased(User)
    stmt = (
        select(Student, user_alias.email)
        .select_from(Student)
        .join(user_alias, user_alias.user_id == Student.user_id, isouter=True)
        .order_by(Student.last_name, Student.first_name)
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(stmt)
    items: list[AdminStudent] = []
    for s, email in res.all():
        items.append(AdminStudent(
            student_id=s.student_id,
            first_name=s.first_name,
            last_name=s.last_name,
            patronymic=s.patronymic,
            confirmed=s.confirmed,
            email=email,
            group_id=s.group_id,
        ))

    return AdminStudentListResponse(students=items, total=total)


@router.get("/teachers", response_model=AdminTeacherListResponse)
async def list_teachers(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    total_res = await db.execute(select(func.count()).select_from(Teacher))
    total = total_res.scalar_one()

    user_alias = aliased(User)
    stmt = (
        select(Teacher, user_alias.email)
        .select_from(Teacher)
        .join(user_alias, user_alias.user_id == Teacher.user_id, isouter=True)
        .order_by(Teacher.last_name, Teacher.first_name)
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(stmt)
    items: list[AdminTeacher] = []
    for t, email in res.all():
        items.append(AdminTeacher(
            teacher_id=t.teacher_id,
            first_name=t.first_name,
            last_name=t.last_name,
            patronymic=t.patronymic,
            confirmed=t.confirmed,
            email=email,
            user_id=t.user_id,
        ))

    return AdminTeacherListResponse(teachers=items, total=total)


@router.post("/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Create a new student (admin only)."""
    student_repo = StudentRepository(db)
    
    # Check if user_id exists and is not already linked to another student
    if student_data.user_id:
        existing = await student_repo.find_by_user_id(student_data.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {student_data.user_id} is already linked to a student"
            )
    
    student = await student_repo.create(
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        patronymic=student_data.patronymic,
        confirmed=student_data.confirmed,
        user_id=student_data.user_id,
        group_id=student_data.group_id,
    )
    await db.commit()
    
    return StudentOut.model_validate(student)


@router.put("/students/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: uuid.UUID,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Update a student (admin only)."""
    student_repo = StudentRepository(db)
    
    # Check if student exists
    existing = await student_repo.find_by_id(student_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )
    
    # Prepare update data using UNSET pattern
    update_kwargs = {}
    
    if student_data.first_name is not UNSET:
        update_kwargs["first_name"] = student_data.first_name
    if student_data.last_name is not UNSET:
        update_kwargs["last_name"] = student_data.last_name
    if student_data.patronymic is not UNSET:
        update_kwargs["patronymic"] = student_data.patronymic
    if student_data.confirmed is not UNSET:
        update_kwargs["confirmed"] = student_data.confirmed
    if student_data.user_id is not UNSET:
        # Check if user_id is being changed to another user that's already linked
        if student_data.user_id is not None:
            existing_with_user = await student_repo.find_by_user_id(student_data.user_id)
            if existing_with_user and existing_with_user.student_id != student_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {student_data.user_id} is already linked to another student"
                )
        update_kwargs["user_id"] = student_data.user_id
    if student_data.group_id is not UNSET:
        update_kwargs["group_id"] = student_data.group_id
    
    updated_student = await student_repo.update(student_id, **update_kwargs)
    await db.commit()
    
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )
    
    return StudentOut.model_validate(updated_student)


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Delete a student (admin only)."""
    student_repo = StudentRepository(db)
    
    # Check if student exists
    existing = await student_repo.find_by_id(student_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )
    
    deleted = await student_repo.delete(student_id)
    await db.commit()
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )
    
    return None

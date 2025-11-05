from fastapi import APIRouter, Depends, Query
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
        ))

    return AdminTeacherListResponse(teachers=items, total=total)

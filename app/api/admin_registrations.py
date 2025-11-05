from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.people.user import User, UserRole
from app.db.models.people.teacher import Teacher
from app.db.models.people.student import Student
from app.db.models.people.registration_request import RegistrationRequest, RegistrationStatus
from app.schemas.registration import (
    RegistrationRequestOut,
    ApproveRegistrationRequest,
    RejectRegistrationRequest,
)

router = APIRouter(prefix="/admin/registrations", tags=["Admin Registrations"])


@router.get("/", response_model=list[RegistrationRequestOut])
async def list_registration_requests(
    status_filter: RegistrationStatus | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    stmt = select(RegistrationRequest)
    if status_filter:
        stmt = stmt.where(RegistrationRequest.status == status_filter)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.patch("/{request_id}/approve", response_model=RegistrationRequestOut)
async def approve_registration_request(
    request_id: str,
    body: ApproveRegistrationRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    # Load request
    stmt = select(RegistrationRequest).where(RegistrationRequest.request_id == request_id)
    result = await db.execute(stmt)
    reg = result.scalar_one_or_none()
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if reg.status != RegistrationStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")

    # Determine final role
    final_role = body.role or reg.requested_role

    # Create or update user by email (or google_sub if provided)
    user_stmt = select(User).where(User.email == reg.email)
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()

    if not user:
        user = User(
            google_sub=reg.google_sub or f"pending:{reg.email}",
            email=reg.email,
            first_name=reg.first_name,
            last_name=reg.last_name,
            patronymic=reg.patronymic,
            role=final_role,
            is_active=True,
        )
        db.add(user)
        await db.flush()
    else:
        user.role = final_role

    # Ensure profile record exists
    if final_role == UserRole.TEACHER:
        t_stmt = select(Teacher).where(Teacher.user_id == user.user_id)
        t_res = await db.execute(t_stmt)
        teacher = t_res.scalar_one_or_none()
        if not teacher:
            teacher = Teacher(
                user_id=user.user_id,
                first_name=user.first_name,
                last_name=user.last_name,
                patronymic=user.patronymic or "",
                confirmed=True,
            )
            db.add(teacher)
        else:
            teacher.confirmed = True

    if final_role == UserRole.STUDENT:
        s_stmt = select(Student).where(Student.user_id == user.user_id)
        s_res = await db.execute(s_stmt)
        student = s_res.scalar_one_or_none()
        if not student:
            student = Student(
                user_id=user.user_id,
                first_name=user.first_name,
                last_name=user.last_name,
                patronymic=user.patronymic,
                confirmed=True,
            )
            db.add(student)
        else:
            student.confirmed = True

    # Update request status
    reg.status = RegistrationStatus.APPROVED
    reg.admin_note = body.admin_note
    reg.decided_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(reg)
    return reg


@router.patch("/{request_id}/reject", response_model=RegistrationRequestOut)
async def reject_registration_request(
    request_id: str,
    body: RejectRegistrationRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    stmt = select(RegistrationRequest).where(RegistrationRequest.request_id == request_id)
    result = await db.execute(stmt)
    reg = result.scalar_one_or_none()
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if reg.status != RegistrationStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")

    reg.status = RegistrationStatus.REJECTED
    reg.admin_note = body.reason
    reg.decided_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(reg)
    return reg

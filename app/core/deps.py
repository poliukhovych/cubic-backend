from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.db.session import async_session_maker
from app.services.course_service import CourseService
from app.services.room_service import RoomService
from app.services.schedule_generation_service import ScheduleService
from app.services.teacher_service import TeacherService
from app.services.group_service import GroupService
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session():
    async with async_session_maker() as session:
        yield session


# --- Individual Service Dependencies ---

async def get_course_service(session: AsyncSession = Depends(get_session)) -> CourseService:
    return CourseService(session)

async def get_teacher_service(session: AsyncSession = Depends(get_session)) -> TeacherService:
    return TeacherService(session)

async def get_group_service(session: AsyncSession = Depends(get_session)) -> GroupService:
    return GroupService(session)

async def get_room_service(session: AsyncSession = Depends(get_session)) -> RoomService:
    return RoomService(session)

async def get_schedule_log_service(
    session: AsyncSession = Depends(get_session)
) -> ScheduleLogService:
    """Dependency for the ScheduleLogService."""
    return ScheduleLogService(session)

async def get_assignment_service(
    session: AsyncSession = Depends(get_session)
) -> AssignmentService:
    """Dependency for the AssignmentService."""
    return AssignmentService(session)


# --- Orchestrator Service Dependency ---

async def get_schedule_service(
    group_service: GroupService = Depends(get_group_service),
    teacher_service: TeacherService = Depends(get_teacher_service),
    room_service: RoomService = Depends(get_room_service),
    course_service: CourseService = Depends(get_course_service),
    schedule_log_service: ScheduleLogService = Depends(get_schedule_log_service),
    assignment_service: AssignmentService = Depends(get_assignment_service)
) -> ScheduleService:
    """
    Dependency for the main ScheduleService (orchestrator).
    Injects all other required services into it.
    """
    return ScheduleService(
        group_service=group_service,
        teacher_service=teacher_service,
        room_service=room_service,
        course_service=course_service,
        schedule_log_service=schedule_log_service,
        assignment_service=assignment_service
    )


# Security dependencies
security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Extract the current user ID from the request.
    This is a placeholder implementation - replace with your actual authentication logic.
    
    For now, it looks for:
    1. Authorization header with Bearer token (JWT parsing would go here)
    2. Session-based authentication via cookies
    3. User ID in request headers (for development/testing)
    
    Returns the user ID if authenticated, None otherwise.
    """
    
    # Method 1: Extract from JWT token (implement JWT parsing here)
    if credentials and credentials.credentials:
        # TODO: Implement JWT token parsing
        # For now, we'll use a simple format: "user_id:token" for demo
        try:
            token_parts = credentials.credentials.split(":")
            if len(token_parts) >= 2 and token_parts[0].startswith("user_"):
                return token_parts[0].replace("user_", "")
        except:
            pass
    
    # Method 2: Extract from session (if using session-based auth)
    # session_id = request.cookies.get("session_id")
    # if session_id:
    #     # Look up user from session store
    #     pass
    
    # Method 3: Extract from custom headers (for development/API keys)
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    
    # Method 4: Extract from query params (not recommended for production)
    user_id = request.query_params.get("user_id")
    if user_id:
        return user_id
    
    return None


def get_authenticated_user_id(
    user_id: Optional[str] = Depends(get_current_user_id)
) -> str:
    """
    Dependency that requires authentication.
    Raises HTTPException if user is not authenticated.
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def get_optional_user_id(
    user_id: Optional[str] = Depends(get_current_user_id)
) -> Optional[str]:
    """
    Dependency that optionally extracts user ID without requiring authentication.
    Used for logging and audit purposes.
    """
    return user_id
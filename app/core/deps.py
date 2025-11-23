from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.db.session import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession

# --- Import Repositories ---
from app.repositories.group_repository import GroupRepository
from app.repositories.teacher_repository import TeacherRepository
from app.repositories.user_repository import UserRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.timeslot_repository import TimeslotRepository
from app.repositories.lesson_repository import LessonRepository
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.constraint_repository import ConstraintRepository
from app.repositories.students_repository import StudentRepository

# --- Import Services ---
from app.services.group_service import GroupService
from app.services.teacher_service import TeacherService
from app.services.user_service import UserService
from app.services.room_service import RoomService
from app.services.course_service import CourseService
from app.services.schedule_service import ScheduleService
from app.services.assignment_service import AssignmentService
from app.services.timeslot_service import TimeslotService
from app.services.teacher_availability_service import TeacherAvailabilityService
from app.services.teacher_preference_service import TeacherPreferenceService
from app.services.group_unavailability_service import GroupUnavailabilityService
from app.services.group_course_service import GroupCourseService
from app.services.teacher_course_service import TeacherCourseService
from app.services.subgroup_constraint_service import SubgroupConstraintService
from app.services.schedule_generation_service import ScheduleGenerationService


async def get_session():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# --- Repository Providers ---

def get_group_repository(
    session: AsyncSession = Depends(get_session)
) -> GroupRepository:
    return GroupRepository(session)

def get_teacher_repository(
    session: AsyncSession = Depends(get_session)
) -> TeacherRepository:
    return TeacherRepository(session)

def get_user_repository(
    session: AsyncSession = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)

def get_room_repository(
    session: AsyncSession = Depends(get_session)
) -> RoomRepository:
    return RoomRepository(session)

def get_course_repository(
    session: AsyncSession = Depends(get_session)
) -> CourseRepository:
    return CourseRepository(session)

def get_schedule_repository(
    session: AsyncSession = Depends(get_session)
) -> ScheduleRepository:
    return ScheduleRepository(session)

def get_assignment_repository(
    session: AsyncSession = Depends(get_session)
) -> AssignmentRepository:
    return AssignmentRepository(session)

def get_timeslot_repository(
    session: AsyncSession = Depends(get_session)
) -> TimeslotRepository:
    return TimeslotRepository(session)

def get_lesson_repository(
    session: AsyncSession = Depends(get_session)
) -> LessonRepository:
    return LessonRepository(session)

def get_availability_repository(
    session: AsyncSession = Depends(get_session)
) -> AvailabilityRepository:
    return AvailabilityRepository(session)

def get_constraint_repository(
    session: AsyncSession = Depends(get_session)
) -> ConstraintRepository:
    return ConstraintRepository(session)

def get_student_repository(
    session: AsyncSession = Depends(get_session)
) -> StudentRepository:
    return StudentRepository(session)


# --- Service Providers ---

def get_group_service(
    repo: GroupRepository = Depends(get_group_repository)
) -> GroupService:
    return GroupService(repo)

def get_teacher_service(
    repo: TeacherRepository = Depends(get_teacher_repository)
) -> TeacherService:
    return TeacherService(repo)

def get_user_service(
    repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repo)

def get_room_service(
    repo: RoomRepository = Depends(get_room_repository)
) -> RoomService:
    return RoomService(repo)

def get_course_service(
    repo: CourseRepository = Depends(get_course_repository)
) -> CourseService:
    return CourseService(repo)

def get_assignment_service(
    repo: AssignmentRepository = Depends(get_assignment_repository)
) -> AssignmentService:
    return AssignmentService(repo)

def get_timeslot_service(
    repo: TimeslotRepository = Depends(get_timeslot_repository),
    lesson_repo: LessonRepository = Depends(get_lesson_repository)
) -> TimeslotService:
    return TimeslotService(repo, lesson_repo)

# Renamed: This is the simple CRUD for the 'schedules' table
def get_schedule_service(
    repo: ScheduleRepository = Depends(get_schedule_repository)
) -> ScheduleService:
    return ScheduleService(repo)

def get_group_course_service(
    repo: ConstraintRepository = Depends(get_constraint_repository)
) -> GroupCourseService:
    return GroupCourseService(repo)

def get_teacher_course_service(
    repo: ConstraintRepository = Depends(get_constraint_repository)
) -> TeacherCourseService:
    return TeacherCourseService(repo)

def get_subgroup_constraint_service(
    repo: ConstraintRepository = Depends(get_constraint_repository)
) -> SubgroupConstraintService:
    return SubgroupConstraintService(repo)

def get_teacher_preference_service(
    repo: AvailabilityRepository = Depends(get_availability_repository)
) -> TeacherPreferenceService:
    return TeacherPreferenceService(repo)

def get_teacher_availability_service(
    repo: AvailabilityRepository = Depends(get_availability_repository),
    timeslot_service: TimeslotService = Depends(get_timeslot_service)
) -> TeacherAvailabilityService:
    return TeacherAvailabilityService(repo, timeslot_service)

def get_group_unavailability_service(
    repo: AvailabilityRepository = Depends(get_availability_repository),
    timeslot_service: TimeslotService = Depends(get_timeslot_service)
) -> GroupUnavailabilityService:
    return GroupUnavailabilityService(repo, timeslot_service)

# --- Orchestrator Provider ---

def get_schedule_generation_service(
    # Catalog services
    group_service: GroupService = Depends(get_group_service),
    teacher_service: TeacherService = Depends(get_teacher_service),
    room_service: RoomService = Depends(get_room_service),
    course_service: CourseService = Depends(get_course_service),
    timeslot_service: TimeslotService = Depends(get_timeslot_service),
    # Constraint services
    group_course_service: GroupCourseService = Depends(get_group_course_service),
    teacher_course_service: TeacherCourseService = Depends(get_teacher_course_service),
    subgroup_constraint_service: SubgroupConstraintService = Depends(get_subgroup_constraint_service),
    # Availability services
    teacher_availability_service: TeacherAvailabilityService = Depends(get_teacher_availability_service),
    teacher_preference_service: TeacherPreferenceService = Depends(get_teacher_preference_service),
    group_unavailability_service: GroupUnavailabilityService = Depends(get_group_unavailability_service),
    # Saving services
    schedule_service: ScheduleService = Depends(get_schedule_service),
    assignment_service: AssignmentService = Depends(get_assignment_service)
) -> ScheduleGenerationService:
    return ScheduleGenerationService(
        group_service=group_service,
        teacher_service=teacher_service,
        room_service=room_service,
        course_service=course_service,
        timeslot_service=timeslot_service,
        group_course_service=group_course_service,
        teacher_course_service=teacher_course_service,
        subgroup_constraint_service=subgroup_constraint_service,
        teacher_availability_service=teacher_availability_service,
        teacher_preference_service=teacher_preference_service,
        group_unavailability_service=group_unavailability_service,
        schedule_service=schedule_service,
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

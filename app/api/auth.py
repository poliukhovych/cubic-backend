"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.oauth2 import id_token
from google.auth.transport import requests

from app.db.session import get_db
from app.db.models.people.user import User, UserRole
from app.db.models.people.teacher import Teacher
from app.db.models.people.student import Student
from app.db.models.people.registration_request import RegistrationRequest, RegistrationStatus
from app.schemas.auth import (
    GoogleAuthRequest, 
    AuthResponse, 
    UserResponse,
    RoleSelectionRequest,
    GoogleCallbackRequest,
    GoogleRegisterRequest,
    GoogleLoginRequest,
    AdminLoginRequest
)
from app.core.security import create_access_token, get_current_user
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth")


@router.post("/google", response_model=AuthResponse)
async def google_auth(
    auth_request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate user with Google OAuth ID token
    
    Flow:
    1. Verify Google ID token
    2. Check if user exists in database
    3. If new user - create User record with selected role
    4. If existing user without role - set role
    5. Create/update corresponding Teacher or Student record
    6. Return JWT token
    """
    
    # Verify Google ID token
    try:
        idinfo = id_token.verify_oauth2_token(
            auth_request.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        google_sub = idinfo['sub']
        email = idinfo['email']
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {str(e)}"
        )
    
    # Check if user exists
    stmt = select(User).where(User.google_sub == google_sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # New user registration - create pending request
    if not user:
        if not auth_request.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role is required for new user registration"
            )
        
        # Check if there's already a pending request
        stmt = select(RegistrationRequest).where(
            (RegistrationRequest.google_sub == google_sub) | (RegistrationRequest.email == email)
        )
        res = await db.execute(stmt)
        existing_req = res.scalar_one_or_none()
        
        if existing_req and existing_req.status == RegistrationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Registration request already submitted and awaiting admin approval"
            )
        
        # Create registration request
        reg = RegistrationRequest(
            google_sub=google_sub,
            email=email,
            first_name=given_name,
            last_name=family_name,
            patronymic=None,
            requested_role=auth_request.role,
            status=RegistrationStatus.PENDING,
        )
        db.add(reg)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Registration submitted and awaiting admin approval"
        )
    
    # Existing user - update role if needed
    else:
        # If user doesn't have role yet, set it
        if user.role is None and auth_request.role:
            user.role = auth_request.role
            
            # Try to find and link existing Teacher/Student record, or create new one
            if auth_request.role == UserRole.TEACHER:
                # Check if teacher record exists with this user_id
                stmt = select(Teacher).where(Teacher.user_id == user.user_id)
                result = await db.execute(stmt)
                teacher = result.scalar_one_or_none()
                
                if not teacher:
                    # Try to find existing teacher by name
                    stmt = select(Teacher).where(
                        (Teacher.user_id.is_(None)) &
                        (Teacher.first_name == user.first_name) &
                        (Teacher.last_name == user.last_name)
                    )
                    result = await db.execute(stmt)
                    teacher = result.scalar_one_or_none()
                    
                    if teacher:
                        # Link existing teacher to this user
                        teacher.user_id = user.user_id
                        logger.info(f"Auto-linked teacher {teacher.teacher_id} to user {user.user_id}")
                    else:
                        # Create new teacher record
                        teacher = Teacher(
                            user_id=user.user_id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            patronymic=user.patronymic or "",
                            status="pending"
                        )
                        db.add(teacher)
            
            elif auth_request.role == UserRole.STUDENT:
                # Check if student record exists with this user_id
                stmt = select(Student).where(Student.user_id == user.user_id)
                result = await db.execute(stmt)
                student = result.scalar_one_or_none()
                
                if not student:
                    # Try to find existing student by name
                    stmt = select(Student).where(
                        (Student.user_id.is_(None)) &
                        (Student.first_name == user.first_name) &
                        (Student.last_name == user.last_name)
                    )
                    result = await db.execute(stmt)
                    student = result.scalar_one_or_none()
                    
                    if student:
                        # Link existing student to this user
                        student.user_id = user.user_id
                        logger.info(f"Auto-linked student {student.student_id} to user {user.user_id}")
                    else:
                        # Create new student record
                        student = Student(
                            user_id=user.user_id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            patronymic=user.patronymic,
                            status="pending"
                        )
                        db.add(student)
            
            await db.commit()
            await db.refresh(user)
        
        # Auto-link existing user with Teacher/Student if has role but not linked
        elif user.role == UserRole.TEACHER:
            stmt = select(Teacher).where(Teacher.user_id == user.user_id)
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                # Try to find existing teacher by name
                stmt = select(Teacher).where(
                    (Teacher.user_id.is_(None)) &
                    (Teacher.first_name == user.first_name) &
                    (Teacher.last_name == user.last_name)
                )
                result = await db.execute(stmt)
                teacher = result.scalar_one_or_none()
                
                if teacher:
                    teacher.user_id = user.user_id
                    await db.commit()
                    logger.info(f"Auto-linked teacher {teacher.teacher_id} to user {user.user_id}")
        
        elif user.role == UserRole.STUDENT:
            stmt = select(Student).where(Student.user_id == user.user_id)
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                # Try to find existing student by name
                stmt = select(Student).where(
                    (Student.user_id.is_(None)) &
                    (Student.first_name == user.first_name) &
                    (Student.last_name == user.last_name)
                )
                result = await db.execute(stmt)
                student = result.scalar_one_or_none()
                
                if student:
                    student.user_id = user.user_id
                    await db.commit()
                    logger.info(f"Auto-linked student {student.student_id} to user {user.user_id}")
    
    # Generate JWT token
    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email,
        role=user.role
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        needs_role_selection=False
    )


@router.post("/admin/login", response_model=AuthResponse)
async def admin_login(
    login_request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Admin login with username/password (non-Google).

    Credentials are provided via environment variables:
    - ADMIN_USERNAME
    - ADMIN_PASSWORD
    Optional profile fields:
    - ADMIN_EMAIL
    - ADMIN_FIRST_NAME
    - ADMIN_LAST_NAME
    """

    if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Admin login is not configured on the server"
        )

    if (
        login_request.username != settings.ADMIN_USERNAME
        or login_request.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )

    # Build admin profile
    admin_email = settings.ADMIN_EMAIL or f"{login_request.username}@admin.local"
    first_name = settings.ADMIN_FIRST_NAME or "Admin"
    last_name = settings.ADMIN_LAST_NAME or "User"
    google_sub = f"admin:{login_request.username}"

    # Try find existing user by email first
    stmt = select(User).where(User.email == admin_email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Fallback: try by constructed google_sub
        stmt = select(User).where(User.google_sub == google_sub)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

    # Create admin user if missing
    if not user:
        user = User(
            google_sub=google_sub,
            email=admin_email,
            first_name=first_name,
            last_name=last_name,
            patronymic=None,
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Ensure role is admin
        if user.role != UserRole.ADMIN:
            user.role = UserRole.ADMIN
            await db.commit()
            await db.refresh(user)

    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email,
        role=user.role
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        needs_role_selection=False
    )


@router.post("/select-role", response_model=AuthResponse)
async def select_role(
    role_request: RoleSelectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Set role for existing user (for users created before role system)
    """
    
    if current_user.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a role"
        )
    
    # Update user role
    current_user.role = role_request.role
    
    # Try to find and link existing Teacher/Student record, or create new one
    if role_request.role == UserRole.TEACHER:
        # Check if there's an existing teacher with matching name but no user_id
        stmt = select(Teacher).where(
            (Teacher.user_id.is_(None)) &
            (Teacher.first_name == current_user.first_name) &
            (Teacher.last_name == current_user.last_name)
        )
        result = await db.execute(stmt)
        teacher = result.scalar_one_or_none()
        
        if teacher:
            # Link existing teacher to this user
            teacher.user_id = current_user.user_id
            logger.info(f"Linked existing teacher {teacher.teacher_id} to user {current_user.user_id}")
        else:
            # Create new teacher record
            teacher = Teacher(
                user_id=current_user.user_id,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                patronymic=current_user.patronymic or "",
                status="pending"
            )
            db.add(teacher)
            logger.info(f"Created new teacher record for user {current_user.user_id}")
    
    elif role_request.role == UserRole.STUDENT:
        # Check if there's an existing student with matching name but no user_id
        stmt = select(Student).where(
            (Student.user_id.is_(None)) &
            (Student.first_name == current_user.first_name) &
            (Student.last_name == current_user.last_name)
        )
        result = await db.execute(stmt)
        student = result.scalar_one_or_none()
        
        if student:
            # Link existing student to this user
            student.user_id = current_user.user_id
            logger.info(f"Linked existing student {student.student_id} to user {current_user.user_id}")
        else:
            # Create new student record
            student = Student(
                user_id=current_user.user_id,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                patronymic=current_user.patronymic,
                status="pending"
            )
            db.add(student)
            logger.info(f"Created new student record for user {current_user.user_id}")
    
    await db.commit()
    await db.refresh(current_user)
    
    # Generate new JWT token with role
    access_token = create_access_token(
        user_id=current_user.user_id,
        email=current_user.email,
        role=current_user.role
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(current_user),
        needs_role_selection=False
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information
    """
    return UserResponse.model_validate(current_user)


@router.post("/google/callback", response_model=AuthResponse)
async def google_oauth_callback(
    callback_request: GoogleCallbackRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Handle Google OAuth callback with authorization code
    
    This endpoint exchanges the authorization code for an ID token,
    then follows the same authentication flow as /auth/google
    
    NOTE: This endpoint requires GOOGLE_CLIENT_SECRET to be configured.
    For client-side authentication, use /auth/google with id_token directly.
    """
    
    import requests as http_requests
    
    # Check if client secret is configured
    if not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Server-side OAuth flow not configured. Use /auth/google with id_token instead."
        )
    
    # Exchange authorization code for tokens
    token_endpoint = "https://oauth2.googleapis.com/token"
    
    token_data = {
        "code": callback_request.code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": callback_request.redirect_uri,
        "grant_type": "authorization_code"
    }
    
    try:
        token_response = http_requests.post(token_endpoint, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        id_token_str = tokens.get("id_token")
        if not id_token_str:
            raise ValueError("No id_token in response")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {str(e)}"
        )
    
    # Verify ID token and extract user info
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        google_sub = idinfo['sub']
        email = idinfo['email']
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {str(e)}"
        )
    
    # Check if user exists
    stmt = select(User).where(User.google_sub == google_sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # New user - needs role selection
    if not user:
        # Create user without role initially
        user = User(
            google_sub=google_sub,
            email=email,
            first_name=given_name,
            last_name=family_name,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Return response indicating role selection needed
        # Generate temporary token (or return without role)
        access_token = create_access_token(
            user_id=user.user_id,
            email=user.email,
            role=UserRole.STUDENT  # Temporary default, will be updated
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
            needs_role_selection=True
        )
    
    # Existing user - check if has role
    if user.role is None:
        # User exists but doesn't have role yet
        access_token = create_access_token(
            user_id=user.user_id,
            email=user.email,
            role=UserRole.STUDENT  # Temporary default
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
            needs_role_selection=True
        )
    
    # Auto-link user with existing Teacher/Student record if not linked yet
    if user.role == UserRole.TEACHER:
        # Check if teacher record exists with this user_id
        stmt = select(Teacher).where(Teacher.user_id == user.user_id)
        result = await db.execute(stmt)
        teacher = result.scalar_one_or_none()
        
        if not teacher:
            # Try to find existing teacher by name
            stmt = select(Teacher).where(
                (Teacher.user_id.is_(None)) &
                (Teacher.first_name == user.first_name) &
                (Teacher.last_name == user.last_name)
            )
            result = await db.execute(stmt)
            teacher = result.scalar_one_or_none()
            
            if teacher:
                # Link existing teacher to this user
                teacher.user_id = user.user_id
                logger.info(f"Auto-linked teacher {teacher.teacher_id} to user {user.user_id}")
            else:
                # Create new teacher record if none exists
                teacher = Teacher(
                    user_id=user.user_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    patronymic=user.patronymic or "",
                    status="active"
                )
                db.add(teacher)
                logger.info(f"Created new teacher record for user {user.user_id}")
            
            await db.commit()
    
    elif user.role == UserRole.STUDENT:
        # Check if student record exists with this user_id
        stmt = select(Student).where(Student.user_id == user.user_id)
        result = await db.execute(stmt)
        student = result.scalar_one_or_none()
        
        if not student:
            # Try to find existing student by name
            stmt = select(Student).where(
                (Student.user_id.is_(None)) &
                (Student.first_name == user.first_name) &
                (Student.last_name == user.last_name)
            )
            result = await db.execute(stmt)
            student = result.scalar_one_or_none()
            
            if student:
                # Link existing student to this user
                student.user_id = user.user_id
                logger.info(f"Auto-linked student {student.student_id} to user {user.user_id}")
            else:
                # Create new student record if none exists
                student = Student(
                    user_id=user.user_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    patronymic=user.patronymic,
                    status="active"
                )
                db.add(student)
                logger.info(f"Created new student record for user {user.user_id}")
            
            await db.commit()
    
    # User exists with role - normal login
    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email,
        role=user.role
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        needs_role_selection=False
    )


@router.post("/register/{role}")
async def register_with_google(
    role: UserRole,
    register_request: GoogleRegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Register new user with Google OAuth (full redirect flow with Classroom scopes)
    
    This endpoint is for NEW user registration only.
    It exchanges authorization code for tokens with full Google Classroom scopes.
    """
    
    import requests as http_requests
    
    # Verify role from path matches role in request
    if register_request.role != role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role mismatch between path and request body"
        )
    
    # Check if OAuth credentials are configured
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured on the server"
        )
    
    if not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_SECRET is not configured on the server. OAuth code flow requires client secret."
        )
    
    # Exchange authorization code for tokens
    token_endpoint = "https://oauth2.googleapis.com/token"
    
    token_data = {
        "code": register_request.code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": register_request.redirect_uri,
        "grant_type": "authorization_code"
    }
    
    try:
        token_response = http_requests.post(token_endpoint, data=token_data, timeout=10)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        id_token_str = tokens.get("id_token")
        access_token_google = tokens.get("access_token")  # For Google Classroom API
        refresh_token_google = tokens.get("refresh_token")  # For long-term access
        
        if not id_token_str:
            raise ValueError("No id_token in response")
        
    except http_requests.exceptions.HTTPError as e:
        error_detail = ""
        status_code = None
        try:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                error_detail = e.response.text or ""
                
                # Log the full error response for debugging
                # Extract full response text for detailed logging
                full_response_text = error_detail
                
                logger.error(
                    f"Google OAuth token exchange failed (register)",
                    extra={
                        "status_code": status_code,
                        "response_text": full_response_text,
                        "url": token_endpoint,
                        "client_id_set": bool(settings.GOOGLE_CLIENT_ID),
                        "client_secret_set": bool(settings.GOOGLE_CLIENT_SECRET),
                        "client_id_preview": settings.GOOGLE_CLIENT_ID[:20] + "..." if settings.GOOGLE_CLIENT_ID and len(settings.GOOGLE_CLIENT_ID) > 20 else settings.GOOGLE_CLIENT_ID,
                        "redirect_uri": register_request.redirect_uri,
                    }
                )
                
                # Try to parse JSON error response
                try:
                    error_json = e.response.json()
                    error_code = error_json.get('error', '')
                    error_description = error_json.get('error_description', '')
                    
                    if error_code or error_description:
                        error_detail = f"{error_code}: {error_description}".strip(": ")
                        
                        # Provide specific guidance based on error type
                        if error_code == 'invalid_client':
                            error_detail = (
                                f"OAuth client not found (invalid_client). "
                                f"This usually means:\n"
                                f"1. GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is incorrect\n"
                                f"2. CLIENT_ID and CLIENT_SECRET don't belong to the same OAuth client\n"
                                f"3. The OAuth client was deleted in Google Cloud Console\n\n"
                                f"Server has client_id set: {bool(settings.GOOGLE_CLIENT_ID)}, "
                                f"client_secret set: {bool(settings.GOOGLE_CLIENT_SECRET)}\n"
                                f"CLIENT_ID preview: {settings.GOOGLE_CLIENT_ID[:30] + '...' if settings.GOOGLE_CLIENT_ID and len(settings.GOOGLE_CLIENT_ID) > 30 else settings.GOOGLE_CLIENT_ID}\n"
                                f"Please verify in Google Cloud Console that these credentials match."
                            )
                        elif error_code == 'invalid_grant':
                            error_detail = f"Invalid authorization code. The code may have expired or already been used. Original error: {error_description}"
                        elif error_code == 'redirect_uri_mismatch':
                            error_detail = f"Redirect URI mismatch. Make sure '{register_request.redirect_uri}' is added to Authorized redirect URIs in Google Cloud Console. Original error: {error_description}"
                        else:
                            # Include full response for unknown errors
                            error_detail = f"{error_code}: {error_description}\nFull response: {full_response_text}"
                except (ValueError, AttributeError) as parse_err:
                    # If JSON parsing fails, use the text response
                    logger.error(f"Failed to parse error response as JSON: {parse_err}, raw response: {full_response_text}")
                    if not error_detail:
                        error_detail = f"Unknown error from Google OAuth API. Raw response: {full_response_text}"
        except Exception as parse_error:
            logger.error(f"Error parsing OAuth error response: {parse_error}")
            error_detail = str(e) if not error_detail else error_detail
        
        # Provide more helpful error messages
        if status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth authentication failed. {error_detail}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {status_code or 'unknown'} - {error_detail}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {str(e)}"
        )
    
    # Verify ID token and extract user info
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        google_sub = idinfo['sub']
        email = idinfo['email']
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {str(e)}"
        )
    
    # Check if user already exists
    stmt = select(User).where(User.google_sub == google_sub)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already registered. Please use login page."
        )

    # If there's already a pending request for this identity/email, return pending
    stmt = select(RegistrationRequest).where(
        (RegistrationRequest.google_sub == google_sub) | (RegistrationRequest.email == email)
    )
    res = await db.execute(stmt)
    existing_req = res.scalar_one_or_none()
    if existing_req and existing_req.status == RegistrationStatus.PENDING:
        return {
            "pending": True,
            "message": "Registration already submitted and awaiting admin approval.",
            "request_id": str(existing_req.request_id),
        }

    # Create a RegistrationRequest in pending status
    reg = RegistrationRequest(
        google_sub=google_sub,
        email=email,
        first_name=given_name,
        last_name=family_name,
        patronymic=None,
        requested_role=role,
        status=RegistrationStatus.PENDING,
    )
    db.add(reg)
    await db.commit()
    return {
        "pending": True,
        "message": "Registration submitted and awaiting admin approval.",
        "request_id": str(reg.request_id),
    }


@router.post("/login")
async def login_with_google(
    login_request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse | dict:
    """
    Login existing user with Google OAuth (full redirect flow)
    
    This endpoint is for EXISTING users only.
    If user not found, returns 404 to redirect to registration.
    """
    
    import requests as http_requests
    
    # Check if OAuth credentials are configured
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured on the server"
        )
    
    if not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_SECRET is not configured on the server. OAuth code flow requires client secret."
        )
    
    # Exchange authorization code for tokens
    token_endpoint = "https://oauth2.googleapis.com/token"
    
    token_data = {
        "code": login_request.code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": login_request.redirect_uri,
        "grant_type": "authorization_code"
    }
    
    try:
        token_response = http_requests.post(token_endpoint, data=token_data, timeout=10)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        id_token_str = tokens.get("id_token")
        if not id_token_str:
            raise ValueError("No id_token in response")
        
    except http_requests.exceptions.HTTPError as e:
        error_detail = ""
        status_code = None
        try:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                error_detail = e.response.text or ""
                
                # Log the full error response for debugging
                full_response_text = error_detail
                
                logger.error(
                    f"Google OAuth token exchange failed (login)",
                    extra={
                        "status_code": status_code,
                        "response_text": full_response_text,
                        "url": token_endpoint,
                        "client_id_set": bool(settings.GOOGLE_CLIENT_ID),
                        "client_secret_set": bool(settings.GOOGLE_CLIENT_SECRET),
                        "client_id_preview": settings.GOOGLE_CLIENT_ID[:20] + "..." if settings.GOOGLE_CLIENT_ID and len(settings.GOOGLE_CLIENT_ID) > 20 else settings.GOOGLE_CLIENT_ID,
                        "redirect_uri": login_request.redirect_uri,
                    }
                )
                
                # Try to parse JSON error response
                try:
                    error_json = e.response.json()
                    error_code = error_json.get('error', '')
                    error_description = error_json.get('error_description', '')
                    
                    if error_code or error_description:
                        error_detail = f"{error_code}: {error_description}".strip(": ")
                        
                        # Provide specific guidance based on error type
                        if error_code == 'invalid_client':
                            error_detail = (
                                f"OAuth client not found (invalid_client). "
                                f"This usually means:\n"
                                f"1. GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is incorrect\n"
                                f"2. CLIENT_ID and CLIENT_SECRET don't belong to the same OAuth client\n"
                                f"3. The OAuth client was deleted in Google Cloud Console\n\n"
                                f"Server has client_id set: {bool(settings.GOOGLE_CLIENT_ID)}, "
                                f"client_secret set: {bool(settings.GOOGLE_CLIENT_SECRET)}\n"
                                f"CLIENT_ID preview: {settings.GOOGLE_CLIENT_ID[:30] + '...' if settings.GOOGLE_CLIENT_ID and len(settings.GOOGLE_CLIENT_ID) > 30 else settings.GOOGLE_CLIENT_ID}\n"
                                f"Please verify in Google Cloud Console that these credentials match."
                            )
                        elif error_code == 'invalid_grant':
                            error_detail = f"Invalid authorization code. The code may have expired or already been used. Original error: {error_description}"
                        elif error_code == 'redirect_uri_mismatch':
                            error_detail = f"Redirect URI mismatch. Make sure '{login_request.redirect_uri}' is added to Authorized redirect URIs in Google Cloud Console. Original error: {error_description}"
                        else:
                            # Include full response for unknown errors
                            error_detail = f"{error_code}: {error_description}\nFull response: {full_response_text}"
                except (ValueError, AttributeError) as parse_err:
                    # If JSON parsing fails, use the text response
                    logger.error(f"Failed to parse error response as JSON: {parse_err}, raw response: {full_response_text}")
                    if not error_detail:
                        error_detail = f"Unknown error from Google OAuth API. Raw response: {full_response_text}"
        except Exception as parse_error:
            logger.error(f"Error parsing OAuth error response: {parse_error}")
            error_detail = str(e) if not error_detail else error_detail
        
        # Provide more helpful error messages
        if status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth authentication failed. {error_detail}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {status_code or 'unknown'} - {error_detail}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {str(e)}"
        )
    
    # Verify ID token and extract user info
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        google_sub = idinfo['sub']
        email = idinfo['email']
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {str(e)}"
        )
    
    # Find existing user
    stmt = select(User).where(User.google_sub == google_sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Check for pending registration
        stmt = select(RegistrationRequest).where(
            RegistrationRequest.google_sub == google_sub
        )
        res = await db.execute(stmt)
        reg = res.scalar_one_or_none()
        if reg and reg.status == RegistrationStatus.PENDING:
            return {
                "pending": True,
                "message": "Your registration is awaiting admin approval.",
                "request_id": str(reg.request_id),
            }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first."
        )
    
    # Auto-link user with existing Teacher/Student record if not linked yet
    if user.role == UserRole.TEACHER:
        # Check if teacher record exists with this user_id
        stmt = select(Teacher).where(Teacher.user_id == user.user_id)
        result = await db.execute(stmt)
        teacher = result.scalar_one_or_none()
        
        if not teacher:
            # Try to find existing teacher by email (first_name + last_name match)
            stmt = select(Teacher).where(
                (Teacher.user_id.is_(None)) &
                (Teacher.first_name == user.first_name) &
                (Teacher.last_name == user.last_name)
            )
            result = await db.execute(stmt)
            teacher = result.scalar_one_or_none()
            
            if teacher:
                # Link existing teacher to this user
                teacher.user_id = user.user_id
                logger.info(f"Auto-linked teacher {teacher.teacher_id} to user {user.user_id}")
            else:
                # Create new teacher record if none exists
                teacher = Teacher(
                    user_id=user.user_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    patronymic=user.patronymic or "",
                    status="active"
                )
                db.add(teacher)
                logger.info(f"Created new teacher record for user {user.user_id}")
            
            await db.commit()
    
    elif user.role == UserRole.STUDENT:
        # Check if student record exists with this user_id
        stmt = select(Student).where(Student.user_id == user.user_id)
        result = await db.execute(stmt)
        student = result.scalar_one_or_none()
        
        if not student:
            # Try to find existing student by email (first_name + last_name match)
            stmt = select(Student).where(
                (Student.user_id.is_(None)) &
                (Student.first_name == user.first_name) &
                (Student.last_name == user.last_name)
            )
            result = await db.execute(stmt)
            student = result.scalar_one_or_none()
            
            if student:
                # Link existing student to this user
                student.user_id = user.user_id
                logger.info(f"Auto-linked student {student.student_id} to user {user.user_id}")
            else:
                # Create new student record if none exists
                student = Student(
                    user_id=user.user_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    patronymic=user.patronymic,
                    status="active"
                )
                db.add(student)
                logger.info(f"Created new student record for user {user.user_id}")
            
            await db.commit()
    
    # Generate JWT token
    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email,
        role=user.role
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        needs_role_selection=False
    )

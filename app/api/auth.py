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
from app.schemas.auth import (
    GoogleAuthRequest, 
    AuthResponse, 
    UserResponse,
    RoleSelectionRequest,
    GoogleCallbackRequest,
    GoogleRegisterRequest,
    GoogleLoginRequest
)
from app.core.security import create_access_token, get_current_user
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
    
    # New user registration
    if not user:
        if not auth_request.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role is required for new user registration"
            )
        
        # Create new user
        user = User(
            google_sub=google_sub,
            email=email,
            first_name=given_name,
            last_name=family_name,
            role=auth_request.role,
            is_active=True
        )
        db.add(user)
        await db.flush()  # Get user_id
        
        # Create corresponding Teacher or Student record
        if auth_request.role == UserRole.TEACHER:
            teacher = Teacher(
                user_id=user.user_id,
                first_name=given_name,
                last_name=family_name,
                patronymic="",  # Can be updated later
                confirmed=False  # Requires admin approval
            )
            db.add(teacher)
        
        elif auth_request.role == UserRole.STUDENT:
            student = Student(
                user_id=user.user_id,
                first_name=given_name,
                last_name=family_name,
                patronymic=None,
                confirmed=False
            )
            db.add(student)
        
        await db.commit()
        await db.refresh(user)
    
    # Existing user - update role if needed
    else:
        # If user doesn't have role yet, set it
        if not user.role and auth_request.role:
            user.role = auth_request.role
            
            # Create corresponding Teacher or Student record if needed
            if auth_request.role == UserRole.TEACHER:
                # Check if teacher record exists
                stmt = select(Teacher).where(Teacher.user_id == user.user_id)
                result = await db.execute(stmt)
                if not result.scalar_one_or_none():
                    teacher = Teacher(
                        user_id=user.user_id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        patronymic="",
                        confirmed=False
                    )
                    db.add(teacher)
            
            elif auth_request.role == UserRole.STUDENT:
                # Check if student record exists
                stmt = select(Student).where(Student.user_id == user.user_id)
                result = await db.execute(stmt)
                if not result.scalar_one_or_none():
                    student = Student(
                        user_id=user.user_id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        patronymic=None,
                        confirmed=False
                    )
                    db.add(student)
            
            await db.commit()
            await db.refresh(user)
    
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
    
    # Create corresponding Teacher or Student record
    if role_request.role == UserRole.TEACHER:
        teacher = Teacher(
            user_id=current_user.user_id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            patronymic="",
            confirmed=False
        )
        db.add(teacher)
    
    elif role_request.role == UserRole.STUDENT:
        student = Student(
            user_id=current_user.user_id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            patronymic=None,
            confirmed=False
        )
        db.add(student)
    
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
            role=None,  # Will be set when user selects role
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
    if not user.role:
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


@router.post("/register/{role}", response_model=AuthResponse)
async def register_with_google(
    role: UserRole,
    register_request: GoogleRegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
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
    
    # Exchange authorization code for tokens
    token_endpoint = "https://oauth2.googleapis.com/token"
    
    token_data = {
        "code": register_request.code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET or "",
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
    
    # Create new user with role
    user = User(
        google_sub=google_sub,
        email=email,
        first_name=given_name,
        last_name=family_name,
        role=role,
        is_active=True
    )
    db.add(user)
    await db.flush()  # Get user_id
    
    # Create corresponding Teacher or Student record
    if role == UserRole.TEACHER:
        teacher = Teacher(
            user_id=user.user_id,
            first_name=given_name,
            last_name=family_name,
            patronymic="",
            confirmed=False  # Requires admin approval
        )
        db.add(teacher)
    
    elif role == UserRole.STUDENT:
        student = Student(
            user_id=user.user_id,
            first_name=given_name,
            last_name=family_name,
            patronymic=None,
            confirmed=False
        )
        db.add(student)
    
    await db.commit()
    await db.refresh(user)
    
    # Generate JWT token for our app
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


@router.post("/login", response_model=AuthResponse)
async def login_with_google(
    login_request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Login existing user with Google OAuth (full redirect flow)
    
    This endpoint is for EXISTING users only.
    If user not found, returns 404 to redirect to registration.
    """
    
    import requests as http_requests
    
    # Exchange authorization code for tokens
    token_endpoint = "https://oauth2.googleapis.com/token"
    
    token_data = {
        "code": login_request.code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET or "",
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first."
        )
    
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

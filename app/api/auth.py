import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Request

from app.schemas.auth import (
    UserResponse, 
    AuthMeResponse, 
    LogoutResponse,
    GoogleAuthRequest,
    TokenResponse
)
from app.db.models.user import UserRole, UserStatus
from app.services.mock_auth_service import MockAuthService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=AuthMeResponse)
async def get_current_user(
    request: Request
) -> AuthMeResponse:
   
    try:
        user_data = getattr(request.state, 'user', None)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        auth_service = MockAuthService()
        user = await auth_service.get_user_by_id(user_data['id'])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return AuthMeResponse(user=UserResponse(**user))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/google/start")
async def google_auth_start():
  
    # TODO: Реалізувати Google OAuth flow
    return {
        "message": "Google OAuth not implemented yet",
        "auth_url": "https://accounts.google.com/oauth/authorize?client_id=..."
    }


@router.get("/google/callback")
async def google_auth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
 
    if error:
        logger.error(f"Google OAuth error: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    try:
        # TODO: Реалізувати обробку Google OAuth callback
        auth_service = MockAuthService()
        
        fake_user = await auth_service.create_or_update_user(
            google_id="dev-google-id",
            name="Dev User",
            email="dev@example.com",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        token = auth_service.create_access_token(fake_user["id"])
        
        return TokenResponse(
            access_token=token,
            expires_in=3600,
            user=UserResponse(**fake_user)
        )
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth callback processing failed"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request
) -> LogoutResponse:
  
    try:
        user_data = getattr(request.state, 'user', None)
        
        if user_data:
            # TODO: Додати токен до чорного списку
            auth_service = MockAuthService()
            await auth_service.revoke_token(user_data.get('token'))
        
        return LogoutResponse()
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return LogoutResponse()


@router.post("/dev/login/{role}")
async def dev_login(
    role: UserRole
) -> TokenResponse:
  
    try:
        auth_service = MockAuthService()
        
        user = await auth_service.create_or_update_user(
            google_id=f"dev-{role.value}",
            name=f"Dev {role.value.title()}",
            email=f"dev-{role.value}@example.com",
            role=role,
            status=UserStatus.ACTIVE
        )
        
        token = auth_service.create_access_token(user["id"])
        
        return TokenResponse(
            access_token=token,
            expires_in=3600,
            user=UserResponse(**user)
        )
        
    except Exception as e:
        logger.error(f"Dev login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dev login failed"
        )


@router.post("/login")
async def login():


    return {
        "message": "Redirect to Google OAuth",
        "redirect_url": "/auth/google/start"
    }

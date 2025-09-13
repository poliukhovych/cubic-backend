import logging
from typing import Optional, List, Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    
    def __init__(
        self,
        app,
        excluded_paths: Optional[List[str]] = None,
        admin_only_paths: Optional[List[str]] = None,
        teacher_only_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        
        self.excluded_paths = excluded_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/auth/google/start",
            "/auth/google/callback",
            "/auth/me"
        ]
        
        self.admin_only_paths = admin_only_paths or [
            "/api/admin",
            "/api/users",
            "/api/system"
        ]
        
        self.teacher_only_paths = teacher_only_paths or [
            "/api/teachers",
            "/api/courses",
            "/api/groups"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        token = self._extract_token(request)
        
        if not token:
            logger.warning(f"Unauthorized access attempt to {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Unauthorized",
                    "detail": "Authentication token required",
                    "status_code": 401
                }
            )
        
        try:
            user = await self._validate_token(token)
            if not user:
                logger.warning(f"Invalid token for {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "Unauthorized",
                        "detail": "Invalid authentication token",
                        "status_code": 401
                    }
                )
            
            if not self._check_permissions(request.url.path, user):
                logger.warning(
                    f"Access denied for user {user.get('id')} to {request.url.path}"
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": "Forbidden",
                        "detail": "Insufficient permissions",
                        "status_code": 403
                    }
                )
            
            request.state.user = user
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Authentication Error",
                    "detail": "Internal authentication error",
                    "status_code": 500
                }
            )
    
    def _is_excluded_path(self, path: str) -> bool:
        return any(path.startswith(excluded) for excluded in self.excluded_paths)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        
        return request.cookies.get("access_token")
    
    async def _validate_token(self, token: str) -> Optional[dict]:
        try:
            from app.services.mock_auth_service import MockAuthService
            
            
            auth_service = MockAuthService()
            token_data = auth_service.verify_token(token)
            
            if not token_data:
                return None
            
           
            user = await auth_service.get_user_by_id(token_data["id"])
            
            if not user or not user.get("is_active", False):
                return None
            
            return {
                "id": str(user["id"]),
                "email": user["email"],
                "role": user["role"].value if user.get("role") else None,
                "status": user["status"].value if user.get("status") else None,
                "token": token
            }
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
    
    def _check_permissions(self, path: str, user: dict) -> bool:
        user_role = user.get("role")
        user_status = user.get("status")
        
        if user_status != "active":
            return False
        
        if user_role == "admin":
            return True
        
        if user_role == "teacher":
            if any(path.startswith(admin_path) for admin_path in self.admin_only_paths):
                return False
            return True
        
        if user_role == "student":
            if (any(path.startswith(admin_path) for admin_path in self.admin_only_paths) or
                any(path.startswith(teacher_path) for teacher_path in self.teacher_only_paths)):
                return False
            return True
        
        return False

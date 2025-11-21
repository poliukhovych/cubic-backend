from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseCustomException(HTTPException):
    """Base class for custom application exceptions"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: Dict[str, Any] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


class ValidationError(BaseCustomException):
    """Raised when input validation fails"""
    
    def __init__(
        self,
        detail: str = "Validation failed",
        field: str = None,
        headers: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            headers=headers
        )
        self.field = field


class NotFoundError(BaseCustomException):
    """Raised when a requested resource is not found"""
    
    def __init__(
        self,
        detail: str = "Resource not found",
        resource_type: str = None,
        resource_id: str = None,
        headers: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
            headers=headers
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class ConflictError(BaseCustomException):
    """Raised when there's a conflict with the current state"""
    
    def __init__(
        self,
        detail: str = "Resource conflict",
        headers: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
            headers=headers
        )


class AuthenticationError(BaseCustomException):
    """Raised when authentication fails"""
    
    def __init__(
        self,
        detail: str = "Authentication failed",
        headers: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
            headers=headers or {"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(BaseCustomException):
    """Raised when authorization fails"""
    
    def __init__(
        self,
        detail: str = "Insufficient permissions",
        required_permission: str = None,
        headers: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR",
            headers=headers
        )
        self.required_permission = required_permission


class DatabaseError(BaseCustomException):
    """Raised when database operation fails"""
    
    def __init__(
        self,
        detail: str = "Database operation failed",
        operation: str = None,
        headers: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
            headers=headers
        )
        self.operation = operation


class ExternalServiceError(BaseCustomException):
    """Raised when external service call fails"""
    
    def __init__(
        self,
        detail: str = "External service unavailable",
        service_name: str = None,
        headers: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="EXTERNAL_SERVICE_ERROR",
            headers=headers
        )
        self.service_name = service_name


class RateLimitError(BaseCustomException):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: int = None,
        headers: Dict[str, Any] = None
    ):
        if retry_after and headers is None:
            headers = {"Retry-After": str(retry_after)}
        
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_ERROR",
            headers=headers
        )
        self.retry_after = retry_after


class BusinessLogicError(BaseCustomException):
    """Raised when business logic validation fails"""
    
    def __init__(
        self,
        detail: str = "Business logic validation failed",
        rule: str = None,
        headers: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BUSINESS_LOGIC_ERROR",
            headers=headers
        )
        self.rule = rule

import traceback
from typing import Callable, Dict, Any
from fastapi import Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import (
    BaseCustomException,
    DatabaseError,
    ValidationError,
    NotFoundError
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global error handling and standardized error responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and handle any exceptions"""
        
        try:
            response = await call_next(request)
            return response
            
        except BaseCustomException as exc:
            # Handle custom application exceptions
            return await self._handle_custom_exception(request, exc)
            
        except RequestValidationError as exc:
            # Handle FastAPI request validation errors
            return await self._handle_request_validation_error(request, exc)
            
        except HTTPException as exc:
            # Handle FastAPI HTTP exceptions
            return await self._handle_http_exception(request, exc)
            
        except PydanticValidationError as exc:
            # Handle Pydantic validation errors
            return await self._handle_validation_error(request, exc)
            
        except SQLAlchemyError as exc:
            # Handle database errors
            return await self._handle_database_error(request, exc)
            
        except ValueError as exc:
            # Handle value errors
            return await self._handle_value_error(request, exc)
            
        except Exception as exc:
            # Handle unexpected errors
            return await self._handle_unexpected_error(request, exc)
    
    async def _handle_custom_exception(
        self, 
        request: Request, 
        exc: BaseCustomException
    ) -> JSONResponse:
        """Handle custom application exceptions"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"Custom exception occurred: {exc.error_code} - {exc.detail}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "error_code": exc.error_code,
                "status_code": exc.status_code,
            }
        )
        
        error_response = {
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "type": "application_error",
                "request_id": request_id,
            }
        }
        
        # Add additional fields for specific exceptions
        if hasattr(exc, 'field') and exc.field:
            error_response["error"]["field"] = exc.field
        if hasattr(exc, 'resource_type') and exc.resource_type:
            error_response["error"]["resource_type"] = exc.resource_type
        if hasattr(exc, 'resource_id') and exc.resource_id:
            error_response["error"]["resource_id"] = exc.resource_id
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=exc.headers or {}
        )
    
    async def _handle_request_validation_error(
        self, 
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI request validation errors"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Format validation errors
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        logger.warning(
            f"Request validation error occurred: {len(validation_errors)} field(s) invalid",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "validation_errors": validation_errors,
            }
        )
        
        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "type": "validation_error",
                "request_id": request_id,
                "details": validation_errors
            }
        }
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response
        )
    
    async def _handle_http_exception(
        self, 
        request: Request, 
        exc: HTTPException
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Determine error code based on status
        error_codes = {
            404: "NOT_FOUND",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            405: "METHOD_NOT_ALLOWED",
            429: "TOO_MANY_REQUESTS",
        }
        
        error_code = error_codes.get(exc.status_code, "HTTP_ERROR")
        
        logger.warning(
            f"HTTP exception occurred: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": exc.status_code,
            }
        )
        
        error_response = {
            "error": {
                "code": error_code,
                "message": str(exc.detail),
                "type": "http_error",
                "request_id": request_id,
            }
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=exc.headers
        )
    
    async def _handle_validation_error(
        self, 
        request: Request, 
        exc: PydanticValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Format validation errors
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        logger.warning(
            f"Validation error occurred: {len(validation_errors)} field(s) invalid",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "validation_errors": validation_errors,
            }
        )
        
        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "type": "validation_error",
                "request_id": request_id,
                "details": validation_errors
            }
        }
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response
        )
    
    async def _handle_database_error(
        self, 
        request: Request, 
        exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle SQLAlchemy database errors"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Determine specific error type
        if isinstance(exc, IntegrityError):
            error_code = "INTEGRITY_CONSTRAINT_VIOLATION"
            message = "Database integrity constraint violation"
            status_code = status.HTTP_409_CONFLICT
        else:
            error_code = "DATABASE_ERROR"
            message = "Database operation failed"
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        logger.error(
            f"Database error occurred: {type(exc).__name__} - {str(exc)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "error_type": type(exc).__name__,
            },
            exc_info=True
        )
        
        error_response = {
            "error": {
                "code": error_code,
                "message": message,
                "type": "database_error",
                "request_id": request_id,
            }
        }
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    async def _handle_value_error(
        self, 
        request: Request, 
        exc: ValueError
    ) -> JSONResponse:
        """Handle ValueError exceptions"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"Value error occurred: {str(exc)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
            }
        )
        
        error_response = {
            "error": {
                "code": "INVALID_VALUE",
                "message": str(exc),
                "type": "value_error",
                "request_id": request_id,
            }
        }
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response
        )
    
    async def _handle_unexpected_error(
        self, 
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """Handle unexpected errors"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.critical(
            f"Unexpected error occurred: {type(exc).__name__} - {str(exc)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "error_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
            },
            exc_info=True
        )
        
        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "type": "internal_error",
                "request_id": request_id,
            }
        }
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )

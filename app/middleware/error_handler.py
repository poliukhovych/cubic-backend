import logging
from typing import Union
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class ErrorResponse:
    
    def __init__(self, error: str, detail: str = None, status_code: int = 500):
        self.error = error
        self.detail = detail
        self.status_code = status_code


def setup_error_handlers(app: FastAPI) -> None:
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning(
            f"HTTP error: {exc.status_code} - {exc.detail} "
            f"for {request.method} {request.url.path}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "detail": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.warning(
            f"Starlette HTTP error: {exc.status_code} - {exc.detail} "
            f"for {request.method} {request.url.path}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "detail": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(
            f"Validation error for {request.method} {request.url.path}: {exc.errors()}"
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "detail": "Invalid request data",
                "errors": exc.errors(),
                "status_code": 422
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error(
            f"Database error for {request.method} {request.url.path}: {str(exc)}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database Error",
                "detail": "Internal server error occurred",
                "status_code": 500
            }
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning(
            f"Pydantic validation error for {request.method} {request.url.path}: {exc.errors()}"
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "detail": "Invalid data format",
                "errors": exc.errors(),
                "status_code": 422
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            f"Unexpected error for {request.method} {request.url.path}: {str(exc)}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "status_code": 500
            }
        )

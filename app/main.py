from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api import health, groups, teachers, courses, auth
from app.db.models.base import Base
from app.db.session import engine
from app.db.models.people.user import User  
from app.db.models.people.teacher import Teacher 
from app.services.course_service import CourseService
from app.services.teacher_service import TeacherService
from app.services.group_service import GroupService
from app.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from app.core.logging import setup_logging
import os


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")
    use_json_logs = os.getenv("USE_JSON_LOGS", "false").lower() == "true"
    
    setup_logging(
        level=log_level,
        log_file=log_file,
        use_json=use_json_logs
    )
    
    # Database initialization
    async with engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "citext";'))
        await conn.run_sync(Base.metadata.create_all)
    
    yield


app = FastAPI(
    title="Cubic Backend API",
    description="API for managing teachers, groups and courses",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware in correct order (outermost first)
# Error handling middleware should be outermost to catch all exceptions
app.add_middleware(ErrorHandlingMiddleware)

# Logging middleware should be next to log all requests/responses
app.add_middleware(LoggingMiddleware)

# CORS middleware
app.add_middleware(  
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose all headers for Google FedCM
)


@app.middleware("http")
async def add_custom_headers(request, call_next):
    response = await call_next(request)
    
    # Add UTF-8 encoding for JSON responses
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["content-type"] = "application/json; charset=utf-8"
    
    return response


app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["teachers"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])

# Simple test endpoint to demo custom exceptions
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError as PydanticValidationError
from app.core.exceptions import NotFoundError

class TestRequest(BaseModel):
    name: str
    age: int

@app.get("/test-middleware/{item_id}")
async def test_middleware(item_id: str):
    """Simple endpoint to test middleware functionality"""
    if item_id == "404":
        raise NotFoundError(detail="Test item not found", resource_type="test", resource_id=item_id)
    elif item_id == "error":
        raise HTTPException(status_code=500, detail="Test internal error")
    elif item_id == "validation":
        # Test Pydantic validation error handling
        raise PydanticValidationError.from_exception_data("TestRequest", [
            {"loc": ("name",), "msg": "Field required", "type": "missing"},
            {"loc": ("age",), "msg": "Input should be a valid integer", "type": "int_parsing", "input": "not_a_number"}
        ])
    else:
        return {"message": f"Success! Item {item_id} found", "middleware_working": True}

@app.post("/test-middleware-validation")
async def test_middleware_validation(request: TestRequest):
    """Test endpoint for validation error handling"""
    return {"message": f"Hello {request.name}, you are {request.age} years old"}


@app.get("/")
async def root():
    return {"message": "Cubic Backend API", "version": "1.0.0"}
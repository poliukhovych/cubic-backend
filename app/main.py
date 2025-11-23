from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api import health, groups, teachers, courses, auth, users, students, rooms, timeslots
from app.db.models.base import Base
from app.db.session import engine
from app.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from app.core.logging import setup_logging
from app.core.config import settings
from app.api import schedules
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

    # Initialize schedule data
    try:
        from app.db.add_schedule_to_db import init_schedule_data
        await init_schedule_data()
    except Exception as e:
        print(f"⚠ Warning: Could not initialize schedule data: {e}")
        # Continue startup even if schedule initialization fails
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
    allow_origins=settings.cors_origins_list,
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
from app.api import admin_registrations
from app.api import admin_people
app.include_router(admin_registrations.router, prefix="/api", tags=["admin-registrations"])
app.include_router(admin_people.router, prefix="/api", tags=["admin-people"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["teachers"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(schedules.router, prefix="/api", tags=["schedules"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(timeslots.router, prefix="/api/timeslots", tags=["timeslots"])

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

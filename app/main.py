from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, teachers, groups, courses, auth, admin, students, teacher
from app.services.course_service import CourseService
from app.services.teacher_service import TeacherService
from app.services.group_service import GroupService
from app.middleware.logging import LoggingMiddleware
from app.middleware.auth import AuthMiddleware
from app.middleware.error_handler import setup_error_handlers
from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    
    application.state.course_service = CourseService()
    application.state.teacher_service = TeacherService()
    application.state.group_service = GroupService()

    yield


app = FastAPI(
    title="Cubic Backend API",
    description="API для управління викладачами, групами та курсами",
    version="1.0.0",
    lifespan=lifespan,
)

setup_error_handlers(app)

app.add_middleware( 
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    AuthMiddleware,
    excluded_paths=[
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/login",
        "/auth/google/start",
        "/auth/google/callback",
        "/auth/me",
        "/auth/dev/login"
    ],
    admin_only_paths=[
        "/api/admin",
        "/api/users",
        "/api/system"
    ],
    teacher_only_paths=[
        "/api/teachers",
        "/api/courses",
        "/api/groups",
        "/api/teacher"
    ]
)


@app.middleware("http")
async def add_encoding_header(request, call_next):
    response = await call_next(request)
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response


app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["teachers"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(teacher.router, prefix="/api/teacher", tags=["teacher"])


@app.get("/")
async def root():
    return {"message": "Cubic Backend API", "version": "1.0.0"}

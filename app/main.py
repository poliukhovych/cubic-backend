from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import health, teachers, groups, courses
from app.db.models.base import Base
from app.db.session import engine
from app.db.models.people.user import User  
from app.db.models.people.teacher import Teacher 
from app.services.course_service import CourseService
from app.services.teacher_service import TeacherService
from app.services.group_service import GroupService


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "citext";'))
        await conn.run_sync(Base.metadata.create_all)

    application.state.course_service = CourseService()
    application.state.group_service = GroupService()

    yield


app = FastAPI(
    title="Cubic Backend API",
    description="API для управління викладачами, групами та курсами",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(  
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_encoding_header(request, call_next):
    response = await call_next(request)
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response


app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["teachers"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])


@app.get("/")
async def root():
    return {"message": "Cubic Backend API", "version": "1.0.0"}

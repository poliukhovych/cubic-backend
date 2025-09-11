from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import health, teachers, groups, courses

app = FastAPI(
    title="Cubic Backend API",
    description="API для управління викладачами, групами та курсами",
    version="1.0.0"
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

import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.session import engine
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def health_check():
    try:
        async with asyncio.timeout(3):
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning(f"Health check: database unavailable: {type(e).__name__}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": "Database unavailable"},
        )
    return {"status": "healthy", "message": "API is running"}

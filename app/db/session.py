from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os

# DATABASE_URL format (asyncpg):
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # True when debugging
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session

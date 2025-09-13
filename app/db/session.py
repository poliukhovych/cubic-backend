from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os

# DATABASE_URL format (asyncpg):
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True, 
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.db.models.base import Base
from app.main import app
from fastapi.testclient import TestClient


# Test database configuration - use main database with transaction isolation
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/schedule_db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Create test session maker
test_session_maker = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_test_db():
    """Set up test database"""
    async with test_engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "citext";'))
        await conn.run_sync(Base.metadata.create_all)
    yield
    # No cleanup needed - we use transaction isolation


@pytest.fixture
async def test_session(setup_test_db):
    """Create a test database session with transaction isolation"""
    async with test_session_maker() as session:
        # Start a transaction that will be rolled back
        trans = await session.begin()
        yield session
        # Rollback the transaction to isolate tests
        await trans.rollback()


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


# Override the session dependency for tests
async def override_get_session():
    async with test_session_maker() as session:
        trans = await session.begin()
        try:
            yield session
        finally:
            await trans.rollback()


# Apply the override
from app.core.deps import get_session
app.dependency_overrides[get_session] = override_get_session

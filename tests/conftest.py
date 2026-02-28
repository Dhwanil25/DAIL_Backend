"""
Test fixtures for the DAIL Backend test suite.

Provides:
- Async test database session (SQLite in-memory for speed)
- Test FastAPI client via httpx.AsyncClient
- Factory fixtures for creating test data
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.database import Base, get_db
from app.main import app

# Use SQLite async for tests (no PostgreSQL required)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client with overridden DB dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ─── Factory Fixtures ───────────────────────────────────────────

@pytest_asyncio.fixture
async def sample_case_data():
    """Return valid case creation payload."""
    return {
        "record_number": "TEST-001",
        "caption": "Doe v. AI Corp",
        "brief_description": "Algorithmic discrimination in hiring",
        "area_of_application": "Employment",
        "issue_text": "Whether AI hiring tool violates Title VII",
        "cause_of_action": "Title VII - Disparate Impact",
        "algorithm_name": "HireBot AI",
        "is_class_action": False,
        "jurisdiction_name": "U.S. District Court",
        "jurisdiction_type": "federal",
        "status_disposition": "pending",
    }


@pytest_asyncio.fixture
async def sample_court_data():
    """Return valid court creation payload."""
    return {
        "name": "United States District Court for the Southern District of New York",
        "short_name": "S.D.N.Y.",
        "citation_string": "S.D.N.Y.",
        "jurisdiction_type": "federal",
        "court_level": "district",
        "state": "NY",
        "country": "US",
    }

"""Integration test fixtures requiring PostgreSQL."""

import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

APP_ROOT = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_ROOT))

os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-for-testing-only-not-production-safe",
)
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://engineering_hub:engineering_hub@localhost:5432/engineering_hub",
)

from db.base import Base, import_all_models  # noqa: E402
from dependencies import get_db  # noqa: E402
from main import app  # noqa: E402

import_all_models()

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

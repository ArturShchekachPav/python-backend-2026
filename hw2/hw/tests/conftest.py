from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from shop_api.main import app
from shop_api.core.db import Base, get_async_session
import pytest_asyncio
from fastapi.testclient import TestClient
import pytest
import 

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

AsyncTestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_db():
    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

app.dependency_overrides[get_async_session] = override_db


@pytest_asyncio.fixture
async def session():
    async with AsyncTestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def item():
    with TestClient(app) as client:
        yield client
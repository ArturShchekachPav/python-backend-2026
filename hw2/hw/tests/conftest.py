from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from shop_api.main import app
from shop_api.core.db import Base, get_async_session
import pytest_asyncio
from fastapi.testclient import TestClient
import pytest
from shop_api.core.base import Item, Cart, CartItem

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
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(autouse=True)
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


@pytest_asyncio.fixture
async def item(session):
    item = Item(name="Test Item", price=10.0)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@pytest_asyncio.fixture
async def deleted_item(session):
    item = Item(name="Test Item", price=10.0, deleted=True)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@pytest_asyncio.fixture
async def cart(session):
    cart = Cart()
    session.add(cart)
    await session.commit()
    await session.refresh(cart)
    return cart


@pytest_asyncio.fixture
async def cart_item(session, item, cart):
    cart_item = CartItem(cart_id=cart.id, item_id=item.id, quantity=1)
    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)
    return cart_item

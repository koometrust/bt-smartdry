import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.hub import Hub
from app.models.user import User

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_test_hubs_and_users(db_session: AsyncSession):
    # Create Hubs
    meru = Hub(name="Meru", location="Meru County", dryer_capacity_kg=200.0)
    tharaka = Hub(name="Tharaka Nithi", location="Tharaka County", dryer_capacity_kg=200.0)
    eldoret = Hub(name="Eldoret", location="Eldoret County", dryer_capacity_kg=200.0)
    
    db_session.add_all([meru, tharaka, eldoret])
    await db_session.flush()

    # Create Users
    admin = User(
        username="admin",
        hashed_password=get_password_hash("AdminPass123!"),
        role="admin",
        hub_id=None,
        preferred_language="en",
        phone_number="+254700000001"
    )
    op_meru = User(
        username="op_meru",
        hashed_password=get_password_hash("MeruPass123!"),
        role="operator",
        hub_id=meru.id,
        preferred_language="en",
        phone_number="+254711000001"
    )
    op_tharaka = User(
        username="op_tharaka",
        hashed_password=get_password_hash("TharakaPass123!"),
        role="operator",
        hub_id=tharaka.id,
        preferred_language="sw",
        phone_number="+254711000002"
    )

    db_session.add_all([admin, op_meru, op_tharaka])
    await db_session.commit()

    return {
        "meru": meru,
        "tharaka": tharaka,
        "eldoret": eldoret,
        "admin": admin,
        "op_meru": op_meru,
        "op_tharaka": op_tharaka
    }

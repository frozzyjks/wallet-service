import pytest
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.main import app
from app.db.deps import get_db
from app.core.database import Base
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    # Без указания scope он будет function по умолчанию
    engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture(autouse=True)
async def setup_db(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def db_session(test_engine):
    connection = await test_engine.connect()
    session_maker = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
    )
    session = session_maker()

    yield session

    await session.close()

    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE wallets CASCADE"))

    await connection.close()

@pytest.fixture
async def client(db_session):
    from httpx import AsyncClient, ASGITransport

    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
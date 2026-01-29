from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from delivery_service.database import get_db
from delivery_service.database.models import Base, Package, PackageType
from delivery_service.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    Session = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with Session() as session:
        yield session


@pytest.fixture(autouse=True)
async def seed_and_clean(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    await db_session.execute(delete(Package))
    await db_session.execute(delete(PackageType))
    await db_session.commit()

    db_session.add_all(
        [
            PackageType(id=1, name="small"),
            PackageType(id=2, name="medium"),
            PackageType(id=3, name="large"),
        ]
    )
    await db_session.commit()

    yield


@pytest.fixture
async def app_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db  # type: ignore[assignment]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()

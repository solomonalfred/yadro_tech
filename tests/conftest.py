import asyncio
import os
import uuid
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import app
from src.db import get_async_session, Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def _engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture()
async def db_session(_engine):
    async_session = async_sessionmaker(
        _engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        trans = await session.begin()
        try:
            yield session
        finally:
            if trans.is_active:
                await trans.rollback()

@pytest.fixture()
async def client(db_session: AsyncSession):
    async def _override():
        yield db_session
    app.dependency_overrides[get_async_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()

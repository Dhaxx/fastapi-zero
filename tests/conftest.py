from contextlib import contextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app import app
from database import get_session
from models import User, table_registry
from security import get_password_hash

SAO_PAULO_TZ = ZoneInfo('America/Sao_Paulo')


@pytest_asyncio.fixture
def client(session):
    def override_get_session():
        return session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


def hook(mapper, connection, target): ...


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 12, 31, tzinfo=SAO_PAULO_TZ)):

    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time.replace(tzinfo=None)

        if hasattr(target, 'updated_at'):
            target.updated_at = time.replace(tzinfo=None)

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest_asyncio.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session):
    user = User(
        username='Ciclano',
        email='Ciclano@gmail.com',
        password=get_password_hash('1234'),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = '1234'

    return user


@pytest_asyncio.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']

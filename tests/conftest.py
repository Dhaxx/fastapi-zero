from contextlib import contextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import app
from database import get_session
from models import User, table_registry

SAO_PAULO_TZ = ZoneInfo('America/Sao_Paulo')


@pytest.fixture
def client(session):
    def override_get_session():
        return session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


def hook(mapper, connection, target): ...


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 12, 31, tzinfo=SAO_PAULO_TZ)):

    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session):
    user = User(username='Ciclano', email='Ciclano@gmail.com', password='1234')
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

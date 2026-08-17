from dataclasses import asdict

import pytest
from conftest import event, hook

from models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Fulano', email='fulano@teste.com', password='fulano123'
        )

        session.add(new_user)
        await session.commit()

    user = await session.get(User, 1)

    assert asdict(user) == {
        'id': 1,
        'username': 'Fulano',
        'email': 'fulano@teste.com',
        'password': 'fulano123',
        'created_at': time.replace(tzinfo=None),
        'updated_at': time.replace(tzinfo=None),
    }


event.listen(User, 'before_insert', hook)

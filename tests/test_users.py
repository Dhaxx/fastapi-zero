from http import HTTPStatus

import pytest

from schemas import UserPublic
from security import create_access_token


@pytest.mark.asyncio
async def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'Fulano',
            'email': 'fulano@gmail.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'Fulano',
        'email': 'fulano@gmail.com',
        'id': 1,
    }


@pytest.mark.asyncio
async def test_get_users(client):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


@pytest.mark.asyncio
async def test_get_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


@pytest.mark.asyncio
async def test_update_user(client, token, user):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Bob',
            'email': 'bob@gmail.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Bob',
        'email': 'bob@gmail.com',
        'id': user.id,
    }


@pytest.mark.asyncio
async def test_delete_user(client, token, user):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted!'}


@pytest.mark.asyncio
async def test_update_user_with_wrong_user(client, token, other_user):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': '1a2b3c4d',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


@pytest.mark.asyncio
async def test_delete_user_with_wrong_user(client, token, other_user):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


# [EXERCÍCIOS]
@pytest.mark.asyncio
async def test_get_user__exercicio(client, user):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }


@pytest.mark.asyncio
async def test_get_user_not_found__exercicio(client):
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found!'}


@pytest.mark.asyncio
async def test_create_user_username_conflict__exercicio(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


@pytest.mark.asyncio
async def test_create_user_email_conflict__exercicio(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


@pytest.mark.asyncio
async def test_get_current_user_not_found__exercicio(client):
    data = {'no-email': 'teste'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_get_current_user_not_exists__exercicio(client):
    data = {'sub': 'nao@existe.com'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_update_integrity_error(client, user, other_user, token):
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }
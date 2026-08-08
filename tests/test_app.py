from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_ola_mundo_retornar_ok_e_html(client):
    response = client.get('/ola_mundo')

    assert response.status_code == HTTPStatus.OK
    assert (
        response.text
        == """
    <html>
      <head>
        <title> Nosso olá mundo!</title>
      </head>
      <body>
        <h1> Olá Mundo </h1>
      </body>
    </html>"""
    )


def test_create_user(client):
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


def test_get_users(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {'username': 'Fulano', 'email': 'fulano@gmail.com', 'id': 1},
        ]
    }


def test_get_user__exercicio(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Fulano',
        'email': 'fulano@gmail.com',
        'id': 1,
    }


def test_get_user_not_found__exercicio(client):
    response = client.get('/users/0')
    
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found!'}


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'Ciclano',
            'email': 'Ciclano@gmail.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Ciclano',
        'email': 'Ciclano@gmail.com',
        'id': 1,
    }


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted!'}


def test_delete_user_not_found__exercicio(client):
    response = client.delete('users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found!'}

def test_update_user_not_found__exercicio(client):
    response = client.put(
        '/users/0',
        json={
            'username': 'Ciclano',
            'email': 'Ciclano@gmail.com',
            'password': '123',
        },)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found!'}
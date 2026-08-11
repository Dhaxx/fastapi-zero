from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas import Message, UserDB, UserList, UserPublic, UserSchema
from database import get_session
from models import User

app = FastAPI()

database = []


@app.get('/', status_code=200)
def read_root():
    return {'message': 'Olá Mundo!'}


@app.get('/ola_mundo', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def ola_mundo():
    return """
    <html>
      <head>
        <title> Nosso olá mundo!</title>
      </head>
      <body>
        <h1> Olá Mundo </h1>
      </body>
    </html>"""


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username already exists" if User.username == user.username else "Email already exists"
        )

    db_user = User(**user.model_dump())

    session.add(db_user)
    session.commit()
    session.refresh()

    return db_user


@app.get('/users', response_model=UserList)
def read_users(session: Session = Depends(get_session)) -> list[UserPublic]:
    return {'users': database}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int, session: Session = Depends(get_session)):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found!'
        )

    return database[user_id]


@app.put('/users/{user_id}', response_model=UserPublic)
def update_users__exercicio(user_id: int, user: UserSchema, session: Session = Depends(get_session)) -> UserPublic:
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found!'
        )

    user_with_id = UserDB(**user.model_dump(exclude_unset=True), id=user_id)
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', response_model=Message)
def delete_users(user_id: int, session: Session = Depends(get_session)) -> Message:
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found!'
        )

    del database[user_id - 1]

    return {'message': 'User deleted!'}

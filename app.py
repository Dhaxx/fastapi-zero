from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_session
from models import User
from schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


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
def create_user(
    user: UserSchema, session: Annotated[Session, Depends(get_session)]
):
    existing_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if existing_user:
        if existing_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )

    db_user = User(**user.model_dump())

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username already exists'
            if session.scalar(
                select(User).where(User.username == user.username)
            )
            else 'Email already exists',
        )


@app.get('/users', response_model=UserList)
def read_users(
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 100,
) -> list[UserPublic]:
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found!'
        )

    return db_user


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Annotated[Session, Depends(get_session)],
) -> UserPublic:
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found!'
        )

    try:
        db_user.username = user.username
        db_user.password = user.password
        db_user.email = user.email
        session.commit()
        session.refresh(db_user)

        return db_user

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@app.delete('/users/{user_id}', response_model=Message)
def delete_users(
    user_id: int, session: Annotated[Session, Depends(get_session)]
) -> Message:
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found!'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted!'}

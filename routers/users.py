from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import User
from schemas import FilterPage, Message, UserList, UserPublic, UserSchema
from security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    existing_user = await session.scalar(
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
    db_user.password = get_password_hash(db_user.password)

    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
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


@router.get('/', response_model=UserList)
async def read_users(
    session: Session, filter_users: Annotated[FilterPage, Query()]
) -> list[UserPublic]:
    query = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )
    users = query.all()
    return {'users': users}


@router.get('/{user_id}', response_model=UserPublic)
async def read_user(user_id: int, session: Session):
    db_user = await session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found!'
        )

    return db_user


@router.put('/{user_id}')
async def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
) -> UserPublic:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@router.delete('/{user_id}')
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
) -> Message:
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted!'}

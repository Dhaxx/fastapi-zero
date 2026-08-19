from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import User
from schemas import Token
from security import create_access_token, get_current_user, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token')
async def get_token(form_data: OAuth2Form, session: Session) -> Token:
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token({'sub': user.email})

    return Token(access_token=access_token, token_type='bearer')


@router.post('/refresh_token')
async def refresh_token(user: CurrentUser) -> Token:
    new_access_token = create_access_token(data={'sub': user.email})

    return Token(access_token=new_access_token, token_type='bearer')

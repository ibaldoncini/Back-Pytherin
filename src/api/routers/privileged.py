# users.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pony.orm import db_session, select
from typing import Optional
from pydantic import Field, BaseModel

from api.models.base import db, DB_User
from api.models.users.user import User, Token, TokenData
from api.utils.login import *
from api.handlers.authentication import *


router = APIRouter()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    email = valid_credentials(token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"},
                            )
    keys = ('username', 'email', 'hashed_password',
            'email_confirmed', 'icon', 'creation_date')
    with db_session:
        try:
            user_tuple = db.get(
                "select * from DB_User where email = $email")
        except:
            raise HTTPException(
                status_code=400, detail="Incorrect email or password")
        user = dict(zip(keys, user_tuple))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user['email_confirmed']:
        raise HTTPException(status_code=400, detail="Unconfirmed user")
    return current_user


@router.get("/users/all")
@db_session
async def dump():
    '''
    Endpoint that show in console the actual state of the users database
    '''
    print(db.select("username,email,email_confirmed from DB_User")[:])
    return ()


@router.get("/users/me", status_code=200)
async def read_users(current_user: User = Depends(get_current_active_user)):
    '''
    API endpoint that serves for testing the token validation. Returns info about
    the user that logged in if validation went well
    '''
    return (current_user)

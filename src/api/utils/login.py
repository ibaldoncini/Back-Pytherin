# login.py
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from pony.orm import db_session, select, commit
from typing import Optional
from passlib.context import CryptContext

from api.models.base import db, DB_User
from api.models.users.user import User, Token, TokenData
from api.handlers.authentication import *
from api.handlers.passwordCheck import pass_checker

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    email = valid_credentials(token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"},
                            )
    keys = ('username', 'email', 'hashedPassword',
            'emailConfirmed', 'icon', 'creationDate')
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
    if not current_user['emailConfirmed']:
        raise HTTPException(status_code=400, detail="Unconfirmed user")
    return current_user


@db_session
def authenticate_user(mail: str, password: str):
    keys = ('username', 'email', 'hashedPassword',
            'emailConfirmed', 'icon', 'creationDate')
    try:
        user_tuple = db.get("select * from DB_User where email = $mail")
    except:
        raise HTTPException(
            status_code=400, detail="Incorrect mail address")
    user = dict(zip(keys, user_tuple))
    if not verify_password(password, user['hashedPassword']):
        return False
    return user

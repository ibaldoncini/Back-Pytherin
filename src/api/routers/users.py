from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from pony.orm import db_session, select
from typing import Optional

from jose import JWTError, jwt


from api.models.base import db, DB_User
from api.models.users.user import User, Token, TokenData
from api.models.users.login import *
from api.functions.passwordCheck import pass_checker


router = APIRouter()


@router.get("/users")
async def read_users(current_user: User = Depends(get_current_active_user)):
    return (current_user)


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/users")
async def register(user: User, password: str):
    if pass_checker(password):
        try:
            with db_session:
                new_user = DB_User(username=user.username,
                                   email=user.email,
                                   hashedPassword=get_password_hash(password),
                                   emailConfirmed=True,
                                   logged=True,
                                   icon=user.icon,
                                   creationDate=datetime.today().strftime('%Y-%m-%d'))
            return {"User registered:": new_user.hashedPassword}
        except:
            raise HTTPException(
                status_code=400, detail="Mail address already in use")
    else:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

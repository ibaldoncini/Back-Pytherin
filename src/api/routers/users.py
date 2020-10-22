# users.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from datetime import datetime, timedelta
from pony.orm import db_session, select
from typing import Optional
from pydantic import Field, BaseModel

from api.models.base import db, DB_User
from api.models.users.user import User, Token, TokenData
from api.utils.login import *
from api.handlers.pass_handler import pass_checker
from api.handlers.authentication import *


router = APIRouter()


@router.post("/users/register", status_code=201)
async def register(user: User, password: str = Body(..., embed=True)):
    """
    Endpoint that allows to register users into the database.
    """
    try:
        with db_session:
            new_user = DB_User(username=user.username,
                               email=user.email,
                               hashed_password=get_password_hash(password),
                               email_confirmed=user.email_confirmed,
                               icon=user.icon,
                               creation_date=datetime.today().strftime('%Y-%m-%d'))
        return {"User registered:": new_user.username}
    except:
        raise HTTPException(
            status_code=400, detail="Mail address already in use")


@router.post("/users", response_model=Token, status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    '''
    LogIn endpoint, first, authenticates the user checking that the
    email and the password submitted by the user are correct.
    Then it creates a valid token for the user.
    '''
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token,
            "token_type": "bearer"}


@router.put("/users/refresh", response_model=Token, status_code=201)
async def refresh_token(email: str = Depends(valid_credentials)):
    """
    Endpoint that creates a new web token.
    As the funciton "updates" creating a new token, it has the PUT method. 
    Need to be logged in to use.
    """
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token,
            "token_type": "bearer"}


@router.post("/token", response_model=Token, status_code=200)
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
        data={"sub": user['email']}, expires_delta=access_token_expires
    )

    return {"access_token": access_token,
            "token_type": "bearer"}

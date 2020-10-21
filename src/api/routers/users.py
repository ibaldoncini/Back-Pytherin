# users.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from datetime import datetime, timedelta
from pony.orm import db_session, select
from typing import Optional
from pydantic import Field, BaseModel

from api.models.base import db, DB_User
from api.models.users.user import User, Token, TokenData
from api.utils.login import *
from api.handlers.passwordCheck import pass_checker
from api.handlers.authentication import *


router = APIRouter()


@router.get("/users/all")
@db_session
async def dump():
    '''
    Endpoint that show in console the actual state of the users database
    '''
    print(db.select("username,email,emailconfirmed,logged from DB_User")[:])
    return ()


@router.get("/users", status_code=200)
async def read_users(current_user: User = Depends(get_current_active_user)):
    '''
    API endpoint that serves for the token validation. Returns info about
    the user that logged in if validation went well
    '''
    return (current_user)


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
    return {"access_token": access_token, "token_type": "bearer"}


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
    actualize_user_status(user['email'])
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/register", status_code=201)
async def register(user: User, password: str = Body(..., embed=True)):
    """
    endpoint that allows to register users into the database.
    """
    if pass_checker(password):
        try:
            with db_session:
                new_user = DB_User(username=user.username,
                                   email=user.email,
                                   hashedPassword=get_password_hash(password),
                                   emailConfirmed=user.emailConfirmed,
                                   logged=True,
                                   icon=user.icon,
                                   creationDate=datetime.today().strftime('%Y-%m-%d'))
            return {"User registered:": new_user.username}
        except:
            raise HTTPException(
                status_code=400, detail="Mail address already in use")
    else:
        raise HTTPException(
            status_code=400, detail="Invalid password")

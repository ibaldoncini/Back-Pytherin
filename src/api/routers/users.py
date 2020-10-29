# users.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from pony.orm import db_session, select, commit
from typing import Optional
from pydantic import Field, BaseModel


from api.models.base import db, DB_User, Validation_Tuple
from api.models.users.user import User, Token, TokenData
from api.utils.login import *
from api.handlers.pass_handler import *
from api.handlers.authentication import *
from api.handlers.param_check import *
from api.handlers.emailvalidation import *


router = APIRouter()


@router.post("/users/register", tags=["Users"], status_code=201)
async def register(user: User):
    """
    User register endpoint
    Params: User data->
      * username : str
      * email : EmailStr
      * password : str
    """
    if check_username_not_in_database(user) and check_email_not_in_database(user):
        with db_session:
            DB_User(
                username=user.username,
                email=user.email,
                hashed_password=get_password_hash(user.password),
                email_confirmed=False,
                icon=user.icon,
                creation_date=datetime.today().strftime("%Y-%m-%d"),
            )

        validator = Validation()
        validator.send_mail(user.email)

        return {
            "message": user.username
            + ", a verification email has"
            + " been sent to "
            + user.email
        }
    else:
        msg = ""
        if not check_username_not_in_database(user):
            msg += "Username already registered "
            raise HTTPException(status_code=409, detail="Username already registered ")
        elif not check_email_not_in_database(user):
            msg += "Email already registered"
            raise HTTPException(status_code=409, detail="Email aready registered")
        return {msg}


# This is a get bc we want the user to be able to use this endpoint from sent link
@router.get("/validate/", tags=["Users"], status_code=200)
async def validate_user(email: str, code: str):
    try:
        with db_session:
            user = DB_User.get(email=email)
            data = db.get("select email,code from Validation_Tuple where email=$email")

            if data[1] != code:
                raise HTTPException(status_code=409, detail="Invalid validation code")

            user = DB_User.get(email=email)
            user.set(email_confirmed=True)
            commit()

        html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Secret voldemort</title>
        </head>
        <body>
            <h1>Verified!</h1>
        </body>
    </html>
    """
        return HTMLResponse(html)
    except:
        raise HTTPException(status_code=404, detail="Email not found")


@router.post("/users", response_model=Token, status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    LogIn endpoint, first, authenticates the user checking that the
    email and the password submitted by the user are correct.
    Then it creates a valid token for the user.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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
        data={"email": user["email"], "username": user["username"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


"""
@router.get("/users", tags=["Users"])
@db_session
async def dump():
    res = []
    for row in db.select("* from DB_User"):
        res.append((row.email, row.email_confirmed))

    print(res.__str__())
    return {"Users: ": res.__str__()}



@router.get("/users/validation_tuple")
@db_session
async def dump_validation():
    res = []
    for row in db.select("email,code from Validation_Tuple")[:]:
        res.append(row)

    print(res.__str__())
    return {"Users: ": res.__str__()}
"""

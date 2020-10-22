# main.py
from fastapi import FastAPI, Depends, Header, HTTPException, Request, Body, status
from pony.orm import db_session, select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

from api.routers import users, privado
from api.models.base import db, DB_User
from api.handlers.pass_handler import *
from api.models.users.user import User, Token, TokenData

"""
Definition of constants and algorithms used in the json web token
"""
SECRET_KEY = "ca26e6bfe7dccf96bb25c729b3ca09990341ca4a5c849959604f567ccae44425"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_token(token: str = Depends(oauth2_scheme)):
    """
    With this function we verify if a token is correct and in use,
    if it fails to check, it returns a message of "invalid credentials".
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"},
                                )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"},
                            )


app = FastAPI()

db.bind('sqlite', 'example.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

app.include_router(users.router)

# en el siguiente router, se encuentran algunas funciones que sirven para
# testear el correcto funcionamiento de los tokens, pues los endpoints
# que estan tienen como dependencia la funcion verify_token definida mas arriba
app.include_router(privado.router, dependencies=[Depends(verify_token)])

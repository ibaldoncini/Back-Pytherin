# main.py
from fastapi import FastAPI, Depends, Header, HTTPException, Request, Body, status
from pony.orm import db_session, select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

from api.routers import users, room_endpoints
from api.routers import privileged
from api.models.base import db, DB_User
from api.handlers.pass_handler import *
from api.models.users.user import User, Token, TokenData
from api.handlers.authentication import verify_token


app = FastAPI()


db.bind('sqlite', 'example.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


app.include_router(users.router)
app.include_router(room_endpoints.router, dependencies=[Depends(verify_token)])
# en el siguiente router, se encuentran algunas funciones que sirven para
# testear el correcto funcionamiento de los tokens, pues los endpoints
# que estan tienen como dependencia la funcion verify_token definida mas arriba
app.include_router(privileged.router, dependencies=[Depends(verify_token)])

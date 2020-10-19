from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from pony.orm import db_session, select
from typing import Optional


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext


from jose import JWTError, jwt


from api.models.base import db, DB_User
from api.models.users.user import User, Token, TokenData
from api.models.users.login import *
from api.functions.passwordCheck import pass_checker

SECRET_KEY = "ca26e6bfe7dccf96bb25c729b3ca09990341ca4a5c849959604f567ccae44425"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@db_session
async def get_user_by_username(uname: str):
    return (db.get("* from DB_User where username = $uname"))


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    keys = ('username', 'email', 'hashedPassword',
            'emailConfirmed', 'logged', 'icon', 'creationDate')
    with db_session:
        try:
            user_tuple = db.get(
                "select * from DB_User where username = $username")
        except:

            raise HTTPException(
                status_code=400, detail="Incorrect username or password")
        user = dict(zip(keys, user_tuple))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user['emailConfirmed']:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@db_session
def authenticate_user(mail: str, password: str):
    keys = ('username', 'email', 'hashedPassword',
            'emailConfirmed', 'logged', 'icon', 'creationDate')
    try:
        user_tuple = db.get("select * from DB_User where email = $mail")
    except:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    user = dict(zip(keys, user_tuple))
    print("\n")
    print(user)
    print("\n")
    if not verify_password(password, user['hashedPassword']):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

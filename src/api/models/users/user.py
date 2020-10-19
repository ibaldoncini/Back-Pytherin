
from pydantic import BaseModel
from typing import Optional
from datetime import date


class User(BaseModel):
    username: str
    email: str
    #password: str
    icon: str = None
    emailConfirmed: Optional[bool] = False
    logged: Optional[bool] = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

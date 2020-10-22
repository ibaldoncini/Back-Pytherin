# user.py
from pydantic import BaseModel
from typing import Optional
from datetime import date


class User(BaseModel):
    '''
    BaseModel for the user, in which we collect the necessary data
    to be able to save the user in the database
    It does not include the password, so it comes separately and is hashed
    once received.
    '''
    username: str
    email: str
    icon: str = None
    email_confirmed: Optional[bool] = False


class Token(BaseModel):
    '''
    Model for tokens, it contains the token_type and the string
    of the token
    '''
    access_token: str
    token_type: str


class TokenData(BaseModel):
    '''
    Optional model, it serves for containing the email
    in the token once decrypted
    '''
    email: Optional[str] = None

# user.py
from pydantic import BaseModel
from typing import Optional
from datetime import date


class User(BaseModel):
    '''
    BaseModel para el usuario, en el tomamos los datos necesarios 
    para poder guardar el usuario en la base de datos
    No incluye la password, asi esta viene por separado y se hashea
    a penas se reciba.
    '''
    username: str
    email: str
    #password: str
    icon: str = None
    emailConfirmed: Optional[bool] = False
    logged: Optional[bool] = True


class Token(BaseModel):
    '''
    Modelo para los tokens, que es el tipo de token
    y el str encriptado en si
    '''
    access_token: str
    token_type: str


class TokenData(BaseModel):
    '''
    Modelo opcional, que sirve para poder guardar
    el email que viene encriptado en el token
    '''
    email: Optional[str] = None

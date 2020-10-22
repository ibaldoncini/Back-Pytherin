# login.py
from fastapi import Depends, HTTPException, status
from pony.orm import db_session, select, commit

from api.models.base import db, DB_User
from api.handlers.authentication import *
from api.handlers.pass_handler import *


@db_session
def authenticate_user(mail: str, password: str):
    keys = ('username', 'email', 'hashed_password',
            'email_confirmed', 'icon', 'creation_date')
    try:
        user_tuple = db.get("select * from DB_User where email = $mail")
    except:
        raise HTTPException(
            status_code=400, detail="Incorrect mail address")
    user = dict(zip(keys, user_tuple))
    if not verify_password(password, user['hashed_password']):
        return False
    return user

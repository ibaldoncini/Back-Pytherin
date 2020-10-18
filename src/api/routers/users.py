from fastapi import APIRouter, Depends
from datetime import datetime,timedelta
from pony.orm import db_session,select
from typing import Optional

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api.models.base import db, DB_User
from api.models.users.user import User
from api.functions.passwordCheck import pass_checker



router = APIRouter()

@router.get("/users") 
async def dump():
  res = {}
  with db_session:
    for row in db.select("* from DB_User"):
      res[row.id] = (row.username,row.email)
  return res








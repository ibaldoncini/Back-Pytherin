from api.models.base import DB_User
from api.functions.param_check import check_email_not_in_database, check_username_not_in_database
from api.models.users.user import User

from datetime import datetime
from fastapi import APIRouter
from pony.orm import db_session,select


router = APIRouter()

@router.post("/users/")
async def register(user : User):

  if (check_username_not_in_database(user) and check_email_not_in_database(user)): 
    with db_session:
      new_user = DB_User(username = user.username,
                        email = user.email,
                        password = user.password,
                        emailConfirmed = False,
                        logged = True,
                        icon = user.icon,
                        creationDate = datetime.today().strftime('%Y-%m-%d'))

    return {"User Registered:":new_user.id}
  else:
    registered_username_msg = "Username already registered "
    registered_email_msg = "Email aready registered "
    msg = ""
    if not check_username_not_in_database(user):
      msg += registered_username_msg
    if not check_email_not_in_database(user):
      msg += registered_email_msg

    return {msg}

      

@router.get("/users") ##solo para testear si los esta guardando bien
async def dump():
  with db_session:
    (select ((u.username,u.email) for u in DB_User if u.logged)).show()
    return

    
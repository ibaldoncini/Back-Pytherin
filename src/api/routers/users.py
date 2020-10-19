from api.models.base import DB_User,db
from api.functions.param_check import check_email_not_in_database,check_username_not_in_database
from api.functions.emailvalidation import Validation
from api.models.users.user import User

from datetime import datetime
from fastapi import APIRouter,HTTPException
from passlib.context import CryptContext
from pony.orm import db_session

SECRET_KEY = "ca26e6bfe7dccf96bb25c729b3ca09990341ca4a5c849959604f567ccae44425"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

router = APIRouter()


# TODO i dont think this belongs here
def verify_password(password, hashed_password):
  return pwd_context.verify(password, hashed_password)


def password_hash(password):
  return pwd_context.hash(password)


@router.post("/users/register",tags=["Users"])
async def register(user : User):
  """
  User register endpoint 
  Params: User data->
    * username : str
    * email : EmailStr
    * password : str
  """
  if (check_username_not_in_database(user) and 
      check_email_not_in_database(user)): 
    with db_session:
      new_user = DB_User(username = user.username,
                        email = user.email,
                        hashedPassword = password_hash(user.password),
                        emailConfirmed = False,
                        logged = True,
                        icon = user.icon,
                        creationDate = datetime.today().strftime('%Y-%m-%d'))

    validator = Validation()
    validator.send_mail(user.email)

    return {"User Registered:": str(new_user.id) + " An email verification has" +
            "been sent to " + user.email}
  else:
    registered_username_msg = "Username already registered "
    registered_email_msg = "Email aready registered "
    msg = ""
    if not check_username_not_in_database(user):
      msg += registered_username_msg
      raise HTTPException(status_code=409,detail=registered_username_msg)
    elif not check_email_not_in_database(user):
      msg += registered_email_msg
      raise HTTPException(status_code=409,detail=registered_email_msg)

    return {msg}

      

@router.get("/users",tags=["Users"])
@db_session
async def dump():
  """
  Dumps id, username and email of all users in database
  """
  res = []
  for row in db.select("* from DB_User"):
    res.append((row.username,row.id,row.email)) 
  
  print(res.__str__())
  return {"Users: " : res.__str__()}


#Esto es como super inseguro no?
#TODO
'''
@router.post("users/validation_code")
async def get_validation_code ():
'''


    
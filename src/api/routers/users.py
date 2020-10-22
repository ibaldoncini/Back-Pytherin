from api.models.base import DB_User, Validation_Tuple,db
from api.functions.param_check import check_email_not_in_database,check_username_not_in_database
from api.functions.emailvalidation import Validation
from api.models.users.user import User

from datetime import datetime
from fastapi import APIRouter,HTTPException
from fastapi.responses import HTMLResponse
from passlib.context import CryptContext
from pony.orm import db_session,commit,select

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
      DB_User(username = user.username,
              email = user.email,
              hashedPassword = password_hash(user.password),
              emailConfirmed = False,
              logged = True,
              icon = user.icon,
              creationDate = datetime.today().strftime('%Y-%m-%d'))

    validator = Validation()
    validator.send_mail(user.email)

    return {"User Registered:": user.username + " A verification email has" +
            " been sent to " + user.email}
  else:
    msg = ""
    if not check_username_not_in_database(user):
      msg += "Username already registered "
      raise HTTPException(status_code=409,detail="Username already registered ")
    elif not check_email_not_in_database(user):
      msg += "Email already registered"
      raise HTTPException(status_code=409,detail="Email aready registered")

    return {msg}


# This is a get bc we want the user to be able to use this endpoint from sent link
@router.get("/validate/",tags=["Users"],status_code=200)
async def validate_user (email : str,code : str):
  try:
    with db_session:
      user = DB_User.get(email=email)
      data = db.get("select email,code from Validation_Tuple where email=$email")

      if data[1] != code:
        raise HTTPException(status_code=409,detail="Invalid validation code")

      user = DB_User.get(email=email)
      user.set(emailConfirmed=True)
      commit()

    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Secret voldemort</title>
        </head>
        <body>
            <h1>Verified!</h1>
        </body>
    </html>
    """
    #todo why is this not returning?
    return HTMLResponse(html)
  except:
    raise HTTPException(status_code=404,detail="Email not found")



@router.get("/users",tags=["Users"])
@db_session
async def dump():
  """
  Dumps id, username and email of all users in database
  """
  res = []
  for row in db.select("* from DB_User"):
    res.append((row.email,row.emailConfirmed))
  
  print(res.__str__())
  return {"Users: " : res.__str__()}


@router.get("/users/validation_tuple")
@db_session
async def dump_validation ():
  res = []
  for row in db.select("email,code from Validation_Tuple")[:]:
    res.append(row)
  
  print(res.__str__())
  return {"Users: " : res.__str__()}



    
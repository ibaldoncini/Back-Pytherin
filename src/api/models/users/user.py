
#from pony.orm.core import desc
from pydantic import BaseModel,Field
from typing import Optional
from pydantic.networks import EmailStr
#from datetime import date

class User(BaseModel):
  username : str = Field(...,min_length=3,max_length=15)
  email : EmailStr
  password : str = Field(...,min_length=8,max_length=54,
    regex="^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).{8,32}$")
  icon : str = None
  emailConfirmed : Optional[bool] = False
  logged : Optional[bool] = True
  #creationDate : date for now, let the date assing automatically


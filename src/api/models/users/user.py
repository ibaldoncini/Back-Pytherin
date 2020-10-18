
from pydantic import BaseModel
from typing import Optional
from datetime import date

class User(BaseModel):
  username : str
  email : str
  password : str
  icon : str = None
  emailConfirmed : Optional[bool] = False
  logged : Optional[bool] = True


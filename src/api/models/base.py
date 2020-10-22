# base.py
from typing import Tuple
from pony.orm import *
from datetime import date
from pydantic.networks import EmailStr

db = Database()

class DB_User(db.Entity):
    username = Required(str)
    email = PrimaryKey(EmailStr)
    hashedPassword = Required(str)
    emailConfirmed = Required(bool)
    logged = Required(bool)#sacar
    icon = Optional(str)
    creationDate = Required(date)

#db.bind('sqlite','example.sqlite', create_db=True)
#db.generate_mapping(create_tables=True)

class Validation_Tuple (db.Entity):
    #How can i map the email to the code?
    email = PrimaryKey(EmailStr)
    code = Required(str)
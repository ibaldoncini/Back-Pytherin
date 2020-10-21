# base.py
from pony.orm import *
from datetime import date
from pydantic.networks import EmailStr

db = Database()

class DB_User(db.Entity):
    id = PrimaryKey(int,auto=True)
    username = Required(str)
    email = Required(EmailStr)
    hashedPassword = Required(str)
    emailConfirmed = Required(bool)
    logged = Required(bool)
    icon = Optional(str)
    creationDate = Required(date)

#db.bind('sqlite','example.sqlite', create_db=True)
#db.generate_mapping(create_tables=True)

class Validation_Tuple (db.Entity):
    username = PrimaryKey(str)
    code = Required(str)
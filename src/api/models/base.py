# base.py
from pony.orm import *
from datetime import date
from pydantic.networks import EmailStr

db = Database()


class DB_User(db.Entity):
    '''
    Entity for the database, the password is stored hashed, and 
    the db uses the user email as PK
    '''
    username = Required(str)
    email = PrimaryKey(str)
    hashed_password = Required(str)
    email_confirmed = Required(bool)
    icon = Optional(str)
    creation_date = Required(date)


class Validation_Tuple (db.Entity):
    """
    Database table used in storing the validation codes
    corresponding to each email registered.
    """
    email = PrimaryKey(EmailStr)
    code = Required(str)

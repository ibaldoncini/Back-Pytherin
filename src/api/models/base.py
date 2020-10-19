# base.py
from pony.orm import *
from datetime import date

db = Database()


class DB_User(db.Entity):
    #id = PrimaryKey(int, auto=True)
    username = Required(str)
    email = PrimaryKey(str)
    hashedPassword = Required(str)
    emailConfirmed = Required(bool)
    logged = Required(bool)
    icon = Optional(str)
    creationDate = Required(date)

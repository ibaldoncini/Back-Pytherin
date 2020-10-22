# base.py
from pony.orm import *
from datetime import date

db = Database()


class DB_User(db.Entity):
    '''
    Entidad para la base de datos, la contraseña se guarda hasheada
    no recolecta un ID para que de esta manera ponyORM tome el 
    email como primary key.
    '''
    username = Required(str)
    email = PrimaryKey(str)
    hashedPassword = Required(str)
    emailConfirmed = Required(bool)
    icon = Optional(str)
    creationDate = Required(date)

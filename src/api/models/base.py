# base.py
from pony.orm import *
from datetime import date
from pydantic.networks import EmailStr
from typing import List

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


class DB_Room(db.Entity):
    """
    Entity for the database, where we keep the status of the room
    and the game_state if begun.
    """
    name = PrimaryKey(str)
    max_players = Required(int)
    owner = Required(str)
    status = Required(int)
    users = Required(Json)
    game = Required(Json)


class Validation_Tuple (db.Entity):
    """
    Database table used in storing the validation codes
    corresponding to each email registered.
    """
    email = PrimaryKey(EmailStr)
    code = Required(str)


def load_from_database():
    pass


def save_game_on_database(
    room_name: str,
    room_status: int,
    death_eaters: List[str],
    voldemort: str,
    minister: str,
    director: str,
    last_minister: str,
    last_director: str,
    de_procs: int,
    fo_procs: int,
    player_list: List[str]
):
    json_save = {"room_status": room_status,
                 "death_eaters": death_eaters,
                 "voldemort": voldemort,
                 "minister": minister,
                 "director": director,
                 "last_minister": last_minister,
                 "last_director": last_director,
                 "de_procs": de_procs,
                 "fo_procs": fo_procs,
                 "player_list": player_list}

    with db_session:
        room = Room.get(name=room_name)
        room.set(game=json_save)

    pass

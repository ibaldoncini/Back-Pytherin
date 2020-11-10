# base.py
from pony.orm import *
from datetime import date
from pydantic.networks import EmailStr
from typing import List
from classes.room import Room, RoomStatus

db = Database()


def define_database_and_entities(**db_params):
    global db

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

    db.bind(**db_params)
    db.generate_mapping(create_tables=True)

    pass


def load_from_database():
    pass


async def save_game_on_database(room: Room):
    json_r = room.dump_game_json()
    room_name = Room.get_name()
    try:
        with db_session:
            if (db.exists("select * from DB_Room where name = $room_name")):
                db_room = db.DB_Room.get(name=room_name)
                if(room.get_status() == RoomStatus.IN_GAME):
                    db.room.set(game=json_r)
                elif (room.get_status() == RoomStatus.PREGAME):
                    db_room.set(status=room.get_status())
                    db_room.set(users=room.get_user_list())
                    db_room.set(game=json_r)
            else:
                db.DB_Room(
                    name=room.get_name(),
                    max_players=room.get_max_players(),
                    owner=room.get_owner,
                    users={},
                    game={}
                )
    except Exception as e:
        print(f"Something went wrong on the db, {e}")


@db_session
async def dump_room(room: Room):
    room_name = room.get_name()
    keys = ('name', 'max_players', 'owner',
            'status', 'users', 'game')
    if (db.exists("select * from DB_Room where name = $room_name")):
        try:
            room_tuple = db.get(
                "select * from DB_Room where name = $room_name")
        except:
            raise HTTPException(
                status_code=400, detail="todo mel")
        cosa = dict(zip(keys, user_tuple))
        return cosa
    else:
        return {"message": "boca"}

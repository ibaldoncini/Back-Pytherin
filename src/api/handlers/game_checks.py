from pony.orm import db_session, select
from api.models.users.user import User
from api.models.base import DB_User

from fastapi import APIRouter, HTTPException, status, Depends, Path
from api.models.room_models import RoomCreationRequest, DiscardRequest, ProposeDirectorRequest, VoteRequest
from api.handlers.authentication import *
from api.utils.room_utils import check_email_status

from classes.room import Room, RoomStatus
from classes.room_hub import RoomHub
from classes.game import Game, Vote
from classes.player import Player
from classes.role_enum import Role
from classes.game_status_enum import GamePhase


async def check_user_in_room_in_game(email, room_name, hub):
    room = hub.get_room_by_name(room_name)
    if room is None:
        raise HTTPException(
            status_code=404, detail="Room not found")
    elif email not in (room.get_user_list()):
        raise HTTPException(
            status_code=403, detail="You're not in this room")
    elif room.status == RoomStatus.PREGAME:
        raise HTTPException(
            status_code=409, detail="The game hasn't started yet")
    elif room.status == RoomStatus.FINISHED:
        raise HTTPException(
            status_code=409, detail="The game is over")
    return room

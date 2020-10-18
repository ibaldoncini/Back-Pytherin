from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from pony.orm import db_session, select
from typing import Optional, List

from api.models.room_models import RoomCreationRequest, JoinRoomRequest
from Room import Room
from RoomHub import RoomHub

router = APIRouter()

hub = RoomHub()


@router.post("/newroom")
async def create_room(room_info: RoomCreationRequest):
    # Check user confirmed email
    # Check for name availability
    global hub
    names = hub.all_rooms()
    if room_info.name in names:
        raise HTTPException(status_code=409, detail="Room name already in use")
    else:
        new_room = Room(room_info.name, room_info.max_players, room_info.email)
        hub.add_room(new_room)
        return {"message": "Created room"}


@router.put("/join")
async def join_room(join_info: JoinRoomRequest):
    # Check user confirmed email
    global hub

    room = hub.get_room_by_name(join_info.room_name)

    message: str
    if (room == None):
        message = "Room doesn't exist"
    elif (not room.isOpen()):
        message = "Room is full or in game"
    else:
        room.user_join(join_info.user)
        message = "joined"

    return {"message": message}

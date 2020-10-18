from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from pony.orm import db_session, select
from typing import Optional, List

from api.models.room_models import RoomCreationRequest, JoinRoomRequest
from Room import Room

router = APIRouter()

rooms: List[Room] = []


@router.post("/newroom")
async def create_room(room_info: RoomCreationRequest):
    # Check user confirmed email
    # Check for name availability
    # Create room or return the missing condition
    new_room = Room(room_info.name, room_info.max_players, room_info.email)
    global room
    rooms.append(new_room)
    return {"message": "Created room"}


@router.put("/join")
async def join_room(join_info: JoinRoomRequest):
    # Check user confirmed email
    global rooms

    room = next((r for r in rooms if r.getName() == join_info.room_name), None)

    message: str
    if (room == None):
        message = "Room doesn't exist"
    elif (not room.isOpen()):
        message = "Room is full or in game"
    else:
        room.user_join(join_info.user)
        message = "joined"

    print(rooms[0].getUserCount())
    return {"message": message}

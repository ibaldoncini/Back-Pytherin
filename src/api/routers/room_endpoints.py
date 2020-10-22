from fastapi import FastAPI, APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status, Response
from pony.orm import db_session, select
from typing import Optional, List
from api.models.base import db
from api.models.room_models import RoomCreationRequest
from Room import Room
from RoomHub import RoomHub
from fastapi.responses import HTMLResponse


router = APIRouter()

hub = RoomHub()


@router.post("/room/new", status_code=status.HTTP_201_CREATED)
async def create_room(room_info: RoomCreationRequest):
    """
    Endpoint for creating a new room.

    Possible respones:\n
            201 when succesfully created.
            401 when email not confirmed.
            409 when the room name is already in use.
            500 raises exception when multiple users have the same e-mail.
    """
    owner = room_info.email
    room_name = room_info.name
    max_players = room_info.max_players

    with db_session:
        try:
            email_confirmed = db.get(
                "select emailConfirmed from DB_User where email = $owner")
        except BaseException:
            raise HTTPException(
                status_code=500, detail="Something went wrong")

    names = hub.all_rooms()

    # if user not logged in raise....
    if not email_confirmed:
        raise HTTPException(
            status_code=401, detail="E-mail not confirmed")
    elif room_name in names:
        raise HTTPException(
            status_code=409, detail="Room name already in use")
    else:
        new_room = Room(room_name, max_players, owner)
        hub.add_room(new_room)
        return {"message": "Room created succesfully"}

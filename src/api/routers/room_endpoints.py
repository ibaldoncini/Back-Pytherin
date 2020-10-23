from fastapi import FastAPI, APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from pony.orm import db_session, select

from api.models.base import db
from api.models.room_models import RoomCreationRequest
from api.handlers.authentication import *
from classes.room import Room
from classes.room_hub import RoomHub


router = APIRouter()

hub = RoomHub()


@router.post("/room/new", status_code=status.HTTP_201_CREATED)
async def create_room(room_info: RoomCreationRequest, email: str = Depends(valid_credentials)):
    """
    Endpoint for creating a new room.

    Possible respones:\n
            201 when succesfully created.
            401 when not logged in.
            403 when email not confirmed.
            409 when the room name is already in use.
            500 when there's an internal error in the database.
    """

    room_name = room_info.name
    max_players = room_info.max_players
    with db_session:
        try:
            email_confirmed = db.get(
                "select email_confirmed from DB_User where email = $email")
        except BaseException:
            raise HTTPException(
                status_code=500, detail="Something went wrong")

    if not email:
        raise HTTPException(
            status_code=401, detail="You need to be logged in to create a new room")
    elif not email_confirmed:
        raise HTTPException(
            status_code=403, detail="E-mail not confirmed")
    elif room_name in (hub.all_rooms()):
        raise HTTPException(
            status_code=409, detail="Room name already in use")
    else:
        new_room = Room(room_name, max_players, email)
        hub.add_room(new_room)
        return {"message": "Room created successfully"}

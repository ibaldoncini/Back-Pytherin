from fastapi import FastAPI, APIRouter, HTTPException, status, Depends, Path
from fastapi.responses import HTMLResponse

from api.models.room_models import RoomCreationRequest
from api.handlers.authentication import *
from api.utils.room_utils import check_email_status
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
    email_confirmed = await check_email_status(email)

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


@router.get("/room/join/{room_name}", status_code=status.HTTP_200_OK)
async def join_room(room_name: str = Path(..., min_length=6, max_length=20, description="The name of the room you want to join"),
                    email: str = Depends(valid_credentials)):
    """
    Endpoint to join a room, it takes the room name as a parameter in the URL, 
    and the access_token in the request headers.

    Possible respones:\n
            20 when succesfully created.
            401 when not logged in.
            403 when email not confirmed.
            404 when the room doesn't exist.
            409 when the user is already in the room.
            403 when the room is full or in-game.
    """

    room = hub.get_room_by_name(room_name)
    if not await check_email_status(email):
        raise HTTPException(status_code=403, detail="E-mail is not confirmed")
    elif not room:
        raise HTTPException(status_code=404, detail="Room not found")
    elif email in room.get_user_list():
        raise HTTPException(
            status_code=409, detail="You are already in this room")
    elif not room.is_open():
        raise HTTPException(status_code=403, detail="Room is full or in-game")
    else:
        await room.user_join(email)
        return {"message": f"Joined {room_name}"}

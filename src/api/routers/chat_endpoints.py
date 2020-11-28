from fastapi import APIRouter, HTTPException, status, Depends, Path, WebSocket, WebSocketDisconnect
from fastapi_utils.tasks import repeat_every
from api.models.room_models import *
from api.handlers.authentication import valid_credentials, get_username_from_token
from api.handlers.game_checks import check_game_preconditions
from api.utils.room_utils import check_email_status, votes_to_json
from datetime import datetime, timedelta
from typing import List
from fastapi.responses import HTMLResponse

from classes.room import Room, RoomStatus
from classes.room_hub import RoomHub
from classes.role_enum import Role
from classes.game_status_enum import GamePhase
from classes.game import Vote, Game
from api.models.base import db, save_game_on_database, load_from_database, remove_room_from_database
from api.routers.room_endpoints import hub

from api.routers.room_endpoints import hub

router = APIRouter()


@router.put("/{room_name}/chat", tags=["Room"], status_code=status.HTTP_201_CREATED)
async def send_message(body: ChatRequest,
                       room_name: str = Path(...,
                                             min_length=6,
                                             max_length=20,
                                             description="The name of the room you want to leave"),
                       username: str = Depends(get_username_from_token)):

    room = hub.get_room_by_name(room_name)
    if room is None:
        raise HTTPException(detail="Room not found",
                            status_code=status.HTTP_404_NOT_FOUND)
    elif room.can_user_chat(username):
        room.post_message(username + " :" + body.msg)
        return {"message": "Message sent succesfully"}
    else:
        raise HTTPException(detail="You can't chat right now",
                            status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @router.websocket("/{room_name}/{token}")
    # async def chat(websocket: WebSocket,
    #                room_name: str = Path(..., min_length=6, max_length=20),
    #                token: str = Path(...)):

    #     # username = get_username_from_token(token)
    #     # if username is None:
    #     #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #     #     print("NO USERNAME")

    #     room = hub.get_room_by_name(room_name)
    #     # if room is None:
    #     #     print("NO ROOM")
    #     #     await websocket.close(code=status.WS_1014_BAD_GATEWAY)

    #     # if username not in room.get_user_list():
    #     #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #     #     print("NOT IN ROOM")
    #     await websocket.accept()
    #     username = token  # await websocket.receive_text()
    #     room.sockets[username] = websocket
    #     print("se conecto el govir de " + username)
    #     await broadcast(room, f"{username} joined the chat", "")

    #     try:
    #         while True:
    #             data = await websocket.receive_text()
    #             print("sent " + data)
    #             await broadcast(room, data, username)
    #     except:
    #         try:
    #             print("se desconecto" + username)
    #             room.sockets.pop(username)
    #         except Exception as f:
    #             print(f)
    #         await broadcast(room, f"{username} left the chat", "")

    # async def broadcast(room: Room, message: str, author: str):
    #     if True:  # room.user_can_user_chat():
    #         separator = ": "
    #         if author == "":
    #             separator = "* "
    #             message += " *"

    #         for ws in list(room.sockets.values()):
    #             msg = author + separator + message
    #             await ws.send_text(msg)
    #     else:
    #         ws = room.sockets[author]
    #         await ws.send_text(msg)

    # html = """
    # <!DOCTYPE html>
    # <html>
    #     <head>
    #         <title>Chat</title>
    #     </head>
    #     <body>
    #         <h1>WebSocket Chat</h1>
    #         <form action="" onsubmit="sendMessage(event)">
    #             <input type="text" id="messageText" autocomplete="off"/>
    #             <button>Send</button>
    #         </form>
    #         <ul id='messages'>
    #         </ul>
    #         <script>
    #             var ws = new WebSocket("ws://localhost:8000/testchat/player1");
    #             ws.onmessage = function(event) {
    #                 var messages = document.getElementById('messages')
    #                 var message = document.createElement('li')
    #                 var content = document.createTextNode(event.data)
    #                 message.appendChild(content)
    #                 messages.appendChild(message)
    #             };
    #             function sendMessage(event) {
    #                 var input = document.getElementById("messageText")
    #                 ws.send(input.value)
    #                 input.value = ''
    #                 event.preventDefault()
    #             }
    #         </script>
    #     </body>
    # </html>
    # """

    # @router.get("/")
    # async def get():
    #     return HTMLResponse(html)

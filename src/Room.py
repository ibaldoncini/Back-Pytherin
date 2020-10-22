from typing import List, Dict
from enum import Enum, unique
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


@unique
class RoomStatus(Enum):
    """Enum for Room class status"""

    PREGAME = 'Pregame'
    IN_GAME = 'In game'
    FINISHED = 'Finished'


class Room:
    """
    This class represents the room, not the game itself.
    It should support the chat, joining, starting a game, etc

    Currently identifying users by their e-mail(str). Maybe not the most optimal approach.
    Using type decorators whenever possible.
    """
    # game: Game -> when game starts

    def __init__(self, name, max_players, owner):
        self.name: str = name
        self.max_players: int = max_players
        self.owner: str = owner
        self.connections: Dict[str, WebSocket] = {}
        self.status: RoomStatus = RoomStatus.PREGAME

    async def user_connect(self, user: str, websocket: WebSocket):
        """
        Add  'user' to the current users list
        user_connect shouldn't be called when is_open == false, but doublecheck anyway.

        Maybe it should return something (confirmation? error?)
        """
        if (self.is_open()):
            await websocket.accept()
            self.connections[user] = websocket

    def is_open(self):
        """
        Returns true when a user can join, false otherwise
        """
        return (len(self.connections) <
                self.max_players and self.status == RoomStatus.PREGAME)

    def user_disconnect(self, user: str):
        """
        Removes a user from the current users list.
        Then passes ownership or removes the room from the hub if necessary
        """
        disconnected_user = self.connections.pop(user, None)
        if (self.connections == {}):
            # WIP
            # server.remove_room(self) -> remove myself from hub
            # del self -> destroy myself
            pass
        elif (self.owner == user):
            self.owner = next(iter(self.connections))

    def get_name(self):
        """ Room name getter"""
        return self.name

    def get_user_count(self):
        """User count getter"""
        return len(self.connections)

    def start_game(self):
        self.status = RoomStatus.IN_GAME
        # Obviously is not finished.

    async def broadcast(self, message: str):
        for user in self.connections:
            await self.connections[user].send_text(message)

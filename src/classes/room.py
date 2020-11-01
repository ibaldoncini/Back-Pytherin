from typing import List
from enum import Enum, unique

from classes.game import Game
from classes.game_status_enum import GamePhase


@unique
class RoomStatus(Enum):
    """Enum for Room class status"""

    PREGAME = "Pregame"
    IN_GAME = "In game"
    FINISHED = "Finished"


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
        self.users: List[str] = []
        self.status: RoomStatus = RoomStatus.PREGAME
        self.game: Game = None

    async def user_join(self, user: str):
        """
        Add  'user' to the current users list
        user_connect shouldn't be called when is_open == false, but doublecheck anyway.

        Maybe it should return something (confirmation? error?)
        """
        if self.is_open():
            self.users.append(user)

    def is_open(self):
        """
        Returns true when a user can join, false otherwise
        """
        return len(self.users) < self.max_players and self.status == RoomStatus.PREGAME

    def user_leave(self, user: str):
        """
        Removes a user from the current users list.
        Then passes ownership or removes the room from the hub if necessary
        """
        self.users.remove(user)
        if self.users == []:
            # WIP
            # server.remove_room(self) -> remove myself from hub
            # del self -> destroy myself
            pass
        elif self.owner == user:
            self.owner = self.users[0]

    def get_name(self):
        """ Room name getter"""
        return self.name

    def get_user_count(self):
        """User count getter"""
        return len(self.users)

    def get_user_list(self):
        """User list getter"""
        return self.users

    def start_game(self):
        self.game = Game(self.users)
        self.status = RoomStatus.IN_GAME
        # Obviously is not finished.

    def get_game(self):
        return self.game

    def set_status(self, status: RoomStatus):
        self.status = status

    def update_status(self):
        game = self.get_game()
        phase = game.get_phase()
        if (phase in [GamePhase.FO_WON, GamePhase.DE_WON]):
            self.set_status(RoomStatus.FINISHED)

from typing import List
from enum import Enum, unique


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
    Try to use type decorators whenever possible.
    """

    def __init__(self, name, max_players, owner):
        self.name: str = name
        self.max_players: int = max_players
        self.owner: str = owner
        self.current_users: List[str] = []
        self.status: RoomStatus = RoomStatus.PREGAME

    def user_join(self, user: str):
        """ 
        Add  'user' to the current users list
        user_join shouldn't be called when isOpen == false, but doublecheck anyway.

        Maybe it should return something
        """
        if (self.is_open()):
            self.current_users.append(user)

    def is_open(self):
        """Returns true when a user can join, false otherwise"""
        return (len(self.current_users) < self.max_players and self.status == RoomStatus.PREGAME)

    def user_leave(self, user):
        """
        Removes a user from the current users list.
        Then passes ownership or removes the room from the hub if necessary
        """
        self.current_users.remove(user)
        if (self.current_users == []):
            # WIP
            # server.remove_room(self) -> remove myself from list of rooms
            # del self -> destroy myself
            pass
        elif (self.owner == user):
            self.owner = self.current_users[0]

    def get_name(self):
        """ Room name getter"""
        return self.name

    def get_user_count(self):
        """User count getter"""
        return len(self.current_users)

    def start_game(self):
        self.status = RoomStatus.IN_GAME
        # Obviously is not finished.

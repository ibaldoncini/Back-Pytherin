from enum import Enum, unique, auto


@unique
class GamePhase(Enum):
    """Enum for Game phase"""

    PROPOSE_DIRECTOR = auto()  # 1
    VOTE_DIRECTOR = auto()  # 2
    MINISTER_DISCARD = auto()  # 3
    DIRECTOR_DISCARD = auto()  # 4
    CAST_DIVINATION = 7
    DE_WON = auto()  # 5
    FO_WON = auto()  # 6

    def __str__(self):
        return self.name

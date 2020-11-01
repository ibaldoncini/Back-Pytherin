from enum import Enum, unique, auto


@unique
class GamePhase(Enum):
    """Enum for Game phase"""

    PROPOSE_DIRECTOR = auto()
    VOTE_DIRECTOR = auto()
    MINISTER_DISCARD = auto()
    DIRECTOR_DISCARD = auto()
    DE_WON = auto()
    FO_WON = auto()

    def __str__(self):
        return self.name

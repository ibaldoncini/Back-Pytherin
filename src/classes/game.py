from enum import Enum
from random import sample, choice
from typing import Dict, List

from classes.player import Player
from classes.board import Board
from classes.role_enum import Role
from classes.loyalty_enum import Loyalty
from classes.deck import Deck
from classes.game_status_enum import GamePhase

class Vote(Enum):
    LUMOS = "Lumos"
    NOX = "Nox"

class Game:
    def __init__(self, users: List[str]):
        self.users: List[str] = users
        self.n_of_players: int = len(users)
        self.players: List[Player] = self.init_players(users)
        self.deck = Deck()
        self.board: Board = Board(self.n_of_players)
        self.minister: Player = choice(self.players)
        self.director: Player = None
        self.last_minister: Player = None
        self.last_director: Player = None
        self.phase: GamePhase = GamePhase.PROPOSE_DIRECTOR
        #!This list should refresh every round
        self.votes : Dict[str,Vote] = dict()


    def init_players(self, users: List[str]):
        # Create empty players
        players: List[Player] = []
        for user in users:
            players.append(Player(user))

        # Calculate number of death eaters
        n_death_eaters = self.n_of_players // 2
        if self.n_of_players % 2 == 0:
            n_death_eaters -= 1

        # Randomize who are the death eaters
        death_eaters = sample(range(0, self.n_of_players), n_death_eaters)
        for i in death_eaters:
            players[i].set_role(Role.DEATH_EATER)
            players[i].set_loyalty(Loyalty.DEATH_EATER)

        # Assign one death eater to be voldemort
        players[choice(death_eaters)].set_role(Role.VOLDEMORT)

        # Assign the rest of the players to be fenix order
        for player in players:
            if player.get_role() == Role.TBD:
                player.set_role(Role.FENIX_ORDER)
                player.set_loyalty(Loyalty.FENIX_ORDER)

        return players


    def get_minister_user(self):
        if self.minister is None:
            return "Undefined"
        else:
            return (self.minister.get_user())


    def get_director_user(self):
        if self.director is None:
            return "Undefined"
        else:
            return (self.director.get_user())


    def get_last_minister_user(self):
        if self.last_minister is None:
            return "Undefined"
        else:
            return (self.last_minister.get_user())


    def get_last_director_user(self):
        if self.last_director is None:
            return "Undefined"
        else:
            return (self.last_director.get_user())


    def get_de_procs(self):
        return (self.board.get_de_procs())


    def get_fo_procs(self):
        return (self.board.get_fo_procs())


    def get_current_players(self):
        """
        method that makes a list from players in game
        """
        unames: list = []
        for player in self.players:
            unames.append(player.get_user())
        return unames


    def __get_player_by_email(self, email: str):
        filtered = filter(lambda p: p.get_user() == email, self.players)
        return (list(filtered)[0])


    def get_player_role(self, email: str):
        return self.__get_player_by_email(email).get_role()


    def get_de_list(self):
        filtered = filter(lambda p:  p.get_loyalty() ==
                          Loyalty.DEATH_EATER, self.players)

        return list(map(lambda p: p.get_user(), filtered))


    def get_voldemort(self):
        filtered = filter(lambda p:  p.get_role() ==
                          Role.VOLDEMORT, self.players)
        return (list(filtered)[0].get_user())

    def get_votes(self):
        return self.votes

    def set_phase(self,phase : GamePhase):
        self.phase = phase

    def register_vote(self,vote,who_votes):
        #?mm vs dsis
        self.votes[who_votes] = vote

    def new_minister(self):
        """
        Method that changes the current minister, it will be called at the
        beggining of a new turn.
        It changes the minister just assigning the role to the next player in
        the list of players of the match.
        """
        self.last_minister = self.minister
        last_minister_index = self.players.index(self.last_minister)
        new_minister_index = (last_minister_index + 1) % self.n_of_players
        self.minister = self.players[new_minister_index]


    #def vote (self):
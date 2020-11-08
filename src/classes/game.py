from enum import Enum
from random import sample, choice
from typing import Dict, List
from collections import Counter

from classes.player import Player
from classes.board import Board
from classes.role_enum import Role
from classes.loyalty_enum import Loyalty
from classes.deck import Deck, Card
from classes.game_status_enum import GamePhase
from classes.spell import Spell


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
        self.cards: List[Card] = self.deck.take_3_cards()
        self.votes: Dict[str, Vote] = dict()

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

    def change_minister(self):
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

    def get_director_user(self):
        if self.director is None:
            return "Undefined"
        else:
            return (self.director.get_user())

    def set_director(self, email):
        if email is None:
            self.director = None
        else:
            self.director = self.__get_player_by_email(email)

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

    def get_cards(self):
        return self.cards

    def discard(self, index):
        self.cards.pop(index)

    def deal_cards(self):
        new_cards = self.deck.take_3_cards()
        self.cards = new_cards

    def get_current_players(self):
        """
        method that makes a list from players in game
        TO DO: check if the lad is a fiambre
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

    def register_vote(self, vote, email):
        self.votes[email] = vote

    def get_phase(self):
        return self.phase

    def set_phase(self, phase: GamePhase):
        self.phase = phase

    def compute_votes(self):
        votes = Counter(self.votes.values())
        lumos_count = votes['Lumos']
        nox_count = votes['Nox']

        if (lumos_count >= nox_count):
            if (self.director.is_voldemort() and self.board.get_de_procs() >= 3):
                self.set_phase(GamePhase.DE_WON)
            else:
                self.set_phase(GamePhase.MINISTER_DISCARD)

        else:
            self.set_director(None)
            self.restart_turn()

    def proc_leftover_card(self):
        card = self.cards.pop(0)
        self.board.proclaim(card)
        self.deal_cards()
        self.spell_check()

    def restart_turn(self):
        self.last_director = self.director
        self.director = None
        self.votes.clear()
        self.change_minister()

        if self.board.get_de_procs() >= 6:
            self.set_phase(GamePhase.DE_WON)
        elif self.board.get_fo_procs() >= 5:
            self.set_phase(GamePhase.FO_WON)
        else:
            self.set_phase(GamePhase.PROPOSE_DIRECTOR)

    def spell_check(self):
        spell = self.board.unlock_spell()
        if (spell == Spell.DIVINATION):
            self.set_phase(GamePhase.CAST_DIVINATION)
        else:
            self.restart_turn()

    def divination(self):
        top_three = self.cards
        self.restart_turn()

        return top_three

from typing import List, Dict
from player import Player
from board import Board
from role_enum import Role
from loyalty_enum import Loyalty
from random import sample, choice
from deck import Deck, Card


class Game:
    def __init__(self, users: List[str]):
        self.users: List[str] = users
        self.n_of_players: int = len(users)
        self.players: List[Player] = self.init_players(users)
        self.deck = Deck()
        self.board: Board = Board(self.n_of_players)
        self.minister: Player = None
        self.director: Player = None

    def init_players(self, users: List[str]):
        # Create empty players
        players: List[Player] = []
        for user in users:
            players.append(Player(user))

        # Calculate number of death eaters
        n_death_eaters = self.n_of_players // 2
        if (self.n_of_players % 2 == 0):
            n_death_eaters -= 1

        # Randomize who are the death eaters
        death_eaters = sample(range(0, self.n_of_players),  n_death_eaters)
        for i in death_eaters:
            players[i].set_role(Role.DEATH_EATER)
            players[i].set_loyalty(Loyalty.DEATH_EATER)

        # Assign one death eater to be voldemort
        players[choice(death_eaters)].set_role(Role.VOLDEMORT)

        # Assign the rest of the players to be fenix order
        for player in players:
            if (player.get_role() == Role.TBD):
                player.set_role(Role.FENIX_ORDER)
                player.set_loyalty(Loyalty.FENIX_ORDER)

        return players

    def dump_game_info(self):
        player_dump: str = "\nUser | Role   | is voldemort | is alive"
        for p in self.players:
            player_dump += f"\n{p.get_user()} | {p.get_role()} | {p.get_is_voldemort()} | {p.get_is_alive()} \n"

        dump: str = f"""
Users: {self.users}
N° of players: {self.n_of_players}
Players: {player_dump}
Deck: {self.deck.cards}
        """
        print(dump)

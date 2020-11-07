from classes.deck import Card
from typing import Dict
from classes.spell import Spell


class Board:
    def __init__(self, n_of_players: int):
        self.de_proclaims: int = 0
        self.fo_proclaims: int = 0
        self.chaos_counter: int = 0
        self.spells: Dict[Spell, int] = self.init_spells(n_of_players)

    def init_spells(self, n_of_players: int):
        if n_of_players >= 9:
            spell_dict = {}
        elif n_of_players >= 7:
            spell_dict = {}
        elif n_of_players >= 5:
            spell_dict = {
                Spell.DIVINATION: 1,
                Spell.AVADA_KEDAVRA: 2
            }

        return spell_dict

    def get_de_procs(self):
        return self.de_proclaims

    def get_fo_procs(self):
        return self.fo_proclaims

    def get_chaos_counter(self):
        return self.chaos_counter

    def increase_chaos(self):
        self.chaos_counter += 1

    def reset_chaos(self):
        self.chaos_counter = 0

    def proclaim(self, card: Card):
        if card == Card.FO:
            self.fo_proclaims += 1
        else:
            self.de_proclaims += 1

    def unlock_spell(self):
        if (self.get_de_procs() == 3 and self.spells[Spell.DIVINATION] > 0):
            self.spells[Spell.DIVINATION] -= 1
            return Spell.DIVINATION
        else:
            return None

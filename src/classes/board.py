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
        else:
            spell_dict = {
                Spell.DIVINATION: 1,
                Spell.AVADA_KEDAVRA: 2,
                Spell.IMPERIUS: 0,
                Spell.CRUCIO: 0
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

    def spell_check(self):
        de_procs = self.get_de_procs()
        if (de_procs == 3 and self.spells[Spell.DIVINATION] > 0):
            self.spells[Spell.DIVINATION] -= 1
            return Spell.DIVINATION
        elif ((de_procs == 4 and self.spells[Spell.AVADA_KEDAVRA] > 1)
                or (de_procs == 5 and self.spells[Spell.AVADA_KEDAVRA] > 0)):
            self.spells[Spell.AVADA_KEDAVRA] -= 1
            return Spell.AVADA_KEDAVRA
        else:
            return None

    def load_spells(self, json):
        self.spells[Spell.DIVINATION] = json[Spell.DIVINATION.value]
        self.spells[Spell.AVADA_KEDAVRA] = json[Spell.AVADA_KEDAVRA.value]
        self.spells[Spell.IMPERIUS] = json[Spell.IMPERIUS.value]
        self.spells[Spell.CRUCIO] = json[Spell.CRUCIO.value]

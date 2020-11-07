from enum import Enum, unique, auto


class Spell(Enum):
    """ Enum for spell representation"""

    DIVINATION = 'Divination'
    AVADA_KEDAVRA = 'Avada kedavra'


def get_spells(n_of_players: int):
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

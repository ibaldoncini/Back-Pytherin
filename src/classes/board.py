from deck import Card


class Board:
    def __init__(self, n_of_players: int):
        self.de_proclaims: int = 0
        self.fo_proclaims: int = 0
        self.chaos_counter: int = 0

    def get_de_proclaims(self):
        return self.de_proclaims

    def get_fo_proclaims(self):
        return self.fo_proclaims

    def get_chaos_counter(self):
        return self.chaos_counter

    def increase_chaos(self):
        self.chaos_counter += 1

    def reset_chaos(self):
        self.chaos_counter = 0

    def proclaim(self, card: Card):
        if (card == Card.FO):
            self.fo_proclaims += 1
        else:
            self.de_proclaims += 1

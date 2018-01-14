"""
Logic for an euchre player whose moves are valid but random.  Used for testing and benchmarking other strategies.
"""
import euchre.valid_moves as vm
from random import random, Random
from euchre.data_model import Suite, Card, PartialRound
from euchre.players.PlayerInterface import PlayerInterface


class RandomPlayer(PlayerInterface):
    """
    Player that randomly plays a card, chooses trump and discards a card

    Arguments:
        seed: seed for random generator to decide on moves
        random_generator: Random generator
    """

    def __init__(self, seed: int = None):
        if seed is None:
            self.seed = random()
        else:
            self.seed = seed
        self.random_generator = Random(self.seed)

    def player_type(self) -> str:
        return "Random: Player plays a random, valid card each turn"

    def dealer_pick_up_trump(self, p_round: PartialRound) -> bool:
        """25% chance dealer will pick up trump"""
        return self.random_generator.randint(0, 3) == 0

    def dealer_discard_card(self, p_round: PartialRound) -> Card:
        """Randomly discard a card"""
        c_ind = self.random_generator.randint(0, 5)
        if c_ind == 5:
            return p_round.flipped_card
        else:
            return p_round.hand[c_ind]

    def call_trump(self, p_round: PartialRound) -> Suite or None:
        """25% chance will call trump, and if so choose a trump"""
        if self.random_generator.randint(0, 3) == 0:
            return self.random_generator.choice([s for s in Suite if s != p_round.flipped_card.suite])
        else:
            return None

    def play_card(self, p_round: PartialRound) -> Card:
        """Play a random valid card"""
        return self.random_generator.choice(vm.valid_trick_moves(p_round))




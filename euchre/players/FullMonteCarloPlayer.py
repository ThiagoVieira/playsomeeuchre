"""
Logic for an euchre player whose moves are calculated based on a MonteCarlo Simulation.
"""
from euchre.data_model import Suite, Card, PartialRound, Round
from euchre.game_simulations import GameTreeSimulation
from euchre.players.BasicPlayer import value_cards, value_hand
from euchre.players.PlayerInterface import PlayerInterface


class FullMonteCarloPlayer(PlayerInterface):

    def __init__(self):
        self.f_round = None
        self.mc_sim = None

    def calculate_game_tree(self, f_round: Round):
        self.f_round = f_round
        self.mc_sim = GameTreeSimulation(f_round.players_cards, f_round.kitty, f_round.trump_caller, f_round.trump, f_round.tricks)
        self.mc_sim.simulate()

    def player_type(self) -> str:
        return "Full Monte Carlo Player knows the entire deck information"

    def dealer_pick_up_trump(self, p_round: PartialRound) -> bool:
        hand_points = value_hand(p_round.hand, p_round.flipped_card.suite)
        return hand_points >= 13

    def dealer_discard_card(self, p_round: PartialRound) -> Card:
        card_values = value_cards(p_round.hand + [p_round.flipped_card], p_round.trump, None)
        card_values.sort(key=lambda x: x[1], reverse=False)  # Sort lowest to highest card value
        return card_values[0][0]

    def call_trump(self, p_round: PartialRound) -> Suite or None:
        # Storing a list of list in the form [Suite, hand_score]
        suite_hand_value = [[s, 0] for s in Suite if s is not p_round.flipped_card.suite]
        for s in suite_hand_value:
            s[1] = value_hand(p_round.hand, s[0])
        suite_hand_value.sort(key=lambda x: x[1], reverse=True)  # Sort highest to lowest card value
        if suite_hand_value[0][1] >= 13:
            return suite_hand_value[0][0]
        return None

    def play_card(self, p_round: PartialRound) -> Card:

        # Look up the best move in the calculated game tree and go from there...
        return None


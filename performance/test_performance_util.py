import euchre.valid_moves as vm
from euchre.players.PlayerInterface import PlayerInterface
from euchre.game_controller import RoundController
from euchre.data_model import Round, CardDeck
from datetime import datetime
from functools import reduce


class RoundResult(object):

    def __init__(self, f_round: Round):
        self.round = f_round
        self.round_filter = 1
        self.trick_filter = [1, 1, 1, 1, 1]

        if self.round.trump is None:
            self.tricks_won_by_round = (None, None, None, None, None)
            self.tricks_won_by_player = (None, None, None, None)
            self.tricks_won_dealer_team = None
            self.points_won = (None, None, None, None)
        else:
            self.tricks_won_by_round = tuple(vm.trick_winner(self.round.tricks[i], self.round.trump) for i in range(5))
            self.tricks_won_by_player = tuple(self.tricks_won_by_round.count(i) for i in range(4))

            dealer_index = self.round.get_dealer_index()
            self.tricks_won_dealer_team = self.tricks_won_by_player[dealer_index] +\
                                            self.tricks_won_by_player[(dealer_index + 2) % 4]

            did_dealer_team_call = (self.round.trump_caller - dealer_index) % 2 == 0
            if self.tricks_won_dealer_team == 5:
                if did_dealer_team_call:
                    self.points_won = (2, 0, 2, 0) if dealer_index % 2 == 0 else (0, 2, 0, 2)
                else:
                    self.points_won = (3, 0, 3, 0) if dealer_index % 2 == 0 else (0, 3, 0, 3)
            elif self.tricks_won_dealer_team in [3, 4]:
                if did_dealer_team_call:
                    self.points_won = (1, 0, 1, 0) if dealer_index % 2 == 0 else (0, 1, 0, 1)
                else:
                    self.points_won = (2, 0, 2, 0) if dealer_index % 2 == 0 else (0, 2, 0, 2)
            elif self.tricks_won_dealer_team in [1, 2]:
                if did_dealer_team_call:
                    self.points_won = (2, 0, 2, 0) if dealer_index % 2 == 1 else (0, 2, 0, 2)
                else:
                    self.points_won = (1, 0, 1, 0) if dealer_index % 2 == 0 else (0, 1, 0, 1)
            elif self.tricks_won_dealer_team == 0:
                if did_dealer_team_call:
                    self.points_won = (3, 0, 3, 0) if dealer_index % 2 == 1 else (0, 3, 0, 3)
                else:
                    self.points_won = (2, 0, 2, 0) if dealer_index % 2 == 1 else (0, 2, 0, 2)

    def reset_filter(self):
        self.round_filter = 1
        self.trick_filter = [1, 1, 1, 1, 1]


class EuchreSim(object):
    def __init__(self, players: [PlayerInterface], runs: int = 1000, card_deck: CardDeck = CardDeck(0)):
        self.players = players
        self.runs = runs
        self.card_deck = card_deck
        self.rounds = []
        self.results = []
        self.sim_time = None
        self.score_time = None

    def simulate(self) -> [RoundResult]:
        start_time = datetime.now()
        for start_index in range(4):
            round_controller = RoundController(self.players, start_index, self.card_deck)
            self.rounds = self.rounds + [round_controller.play() for _ in range(self.runs)]
        self.sim_time = datetime.now()-start_time
        start_time = datetime.now()
        self.results = [RoundResult(r) for r in self.rounds]
        self.score_time = datetime.now()-start_time
        return self.results


def summary_results(round_results: [RoundResult]):
    """Create summary statistics from a list of round results"""
    results = list(filter(lambda x: x.round_filter == 1 and x.tricks_won_dealer_team is not None, round_results))
    add_func = lambda x, y: (x[0] + y[0], x[1] + y[1], x[2] + y[2], x[3] + y[3])
    game_func = lambda x: (int(x[0] > 0), int(x[1] > 0), int(x[2] > 0), int(x[3] > 0))
    points_won = reduce(add_func, [r.points_won for r in results])
    games_won = reduce(add_func, [game_func(r.points_won) for r in results])
    tricks_won = reduce(add_func, [r.tricks_won_by_player for r in results])
    return points_won, games_won, tricks_won


def print_results(round_results: [RoundResult]):
    """Print summary statistics for a list of round results in the simulation"""
    results = summary_results(round_results)
    print("Number of results with values: " + str(len(results)))
    print("Points won by player: " + str(results[0]))
    print("Games won by player: " + str(results[1]))
    print("Tricks won by player: " + str(results[2]))



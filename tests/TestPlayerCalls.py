import unittest
from euchre.data_model import PartialRound
from euchre.players.PlayerInterface import PlayerInterface
from euchre.players.RandomPlayer import RandomPlayer
from euchre.players.BasicPlayer import BasicPlayer
from euchre.players.RulePlayer import RulePlayer
from euchre.serializer import json_to_game


class TestPlayerCalls(unittest.TestCase):
    def test_random_player(self):
        self.__execute_player_calls(RandomPlayer())

    def test_basic_player(self):
        self.__execute_player_calls(BasicPlayer())

    def test_rule_player(self):
        self.__execute_player_calls(RulePlayer())

    def __execute_player_calls(self, player: PlayerInterface):
        # test ability to pick up trump
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 11, 5, 10, 25], "dropped_card": null}, ' \
                   '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
                   '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
                   '{"index": 3, "order": 3, "hand": [0, 2, 18, 19, 17], "dropped_card": null}], ' \
                   '"deck": [28, 4, 8, 21], "tricks": [], "trump_caller": null, "trump": null}'
        f_round = PartialRound.from_round(json_to_game(json_str), 3)
        move = player.dealer_pick_up_trump(f_round)
        self.assertIn(move, [False, True], "Must return a boolean of whether to pick up card")

        # test ability for dealer to discard card
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 11, 5, 10, 25], "dropped_card": null}, ' \
                   '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
                   '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
                   '{"index": 3, "order": 3, "hand": [0, 2, 18, 19, 17], "dropped_card": null}], ' \
                   '"deck": [28, 4, 8, 21], "tricks": [], "trump_caller": 0, "trump": 0}'
        f_round = PartialRound.from_round(json_to_game(json_str), 0)
        move = player.dealer_discard_card(f_round)
        self.assertIn(move.value, [1, 11, 5, 10, 25, 28], "Invalid dealer picking up card ")

        # Test ability to call trump
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 11, 5, 10, 25], "dropped_card": null}, ' \
                   '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
                   '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
                   '{"index": 3, "order": 3, "hand": [0, 2, 18, 19, 17], "dropped_card": null}], ' \
                   '"deck": [28, 4, 8, 21], "tricks": [], "trump_caller": null, "trump": null}'
        f_round = PartialRound.from_round(json_to_game(json_str), 0)
        move = player.call_trump(f_round)
        self.assertIn(move, [None, 0, 1, 2], "Invalid calling trump move")  # Can't call trump of card dropped

        # test ability to make a move
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 11, 5, 10, 25], "dropped_card": null}, ' \
                   '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
                   '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
                   '{"index": 3, "order": 3, "hand": [0, 2, 18, 19, 17], "dropped_card": null}], ' \
                   '"deck": [28, 4, 8, 21], "tricks": [{"start_index": 0, "cards":[1]}], ' \
                   '"trump_caller": 0, "trump": 0}'
        f_round = PartialRound.from_round(json_to_game(json_str), 1)
        move = player.play_card(f_round)
        self.assertIn(move.value, [26, 16, 20, 13, 29], "Incorrect move made")


if __name__ == '__main__':
    unittest.main()

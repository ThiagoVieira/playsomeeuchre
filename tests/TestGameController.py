import unittest
from euchre.data_model import CardDeck, GameAction, Game
from euchre.game_controller import GameController
from euchre.players.RandomPlayer import RandomPlayer
from euchre.players.BasicPlayer import BasicPlayer
from euchre.players.RulePlayer import RulePlayer
from euchre.serializer import is_game_json_valid, game_to_json


class TestGameController(unittest.TestCase):

    def test_random_game(self):
        controller = GameController([RandomPlayer(0) for _ in range(4)], CardDeck(0))
        controller.play()
        self.assertEqual(controller.game.current_action, GameAction.GAME_OVER)
        for r in controller.game.rounds:
            is_game_json_valid(game_to_json(r))

    def test_web_player(self):
        controller = GameController([RandomPlayer(0) for _ in range(4)], CardDeck(0))
        controller.play()
        self.assertEqual(controller.game.current_action, GameAction.GAME_OVER)
        for r in controller.game.rounds:
            is_game_json_valid(game_to_json(r))

    def test_repeatability_game(self):
        controller1 = GameController([RandomPlayer(0) for _ in range(4)], CardDeck(0))
        controller1.play()
        controller2 = GameController([RandomPlayer(0) for _ in range(4)], CardDeck(0))
        controller2.play()
        self.__check_two_games_equal(controller1.game, controller2.game)

    def test_basic_game(self):
        controller1 = GameController([BasicPlayer() for _ in range(4)], CardDeck(0))
        controller1.play()
        self.assertEqual(controller1.game.current_action, GameAction.GAME_OVER)
        for r in controller1.game.rounds:
            is_game_json_valid(game_to_json(r))
        controller2 = GameController([BasicPlayer() for _ in range(4)], CardDeck(0))
        controller2.play()
        self.__check_two_games_equal(controller1.game, controller2.game)

    def test_rule_game(self):
        controller1 = GameController([RulePlayer() for _ in range(4)], CardDeck(0))
        controller1.play()
        self.assertEqual(controller1.game.current_action, GameAction.GAME_OVER)
        for r in controller1.game.rounds:
            is_game_json_valid(game_to_json(r))
        controller2 = GameController([RulePlayer() for _ in range(4)], CardDeck(0))
        controller2.play()
        self.__check_two_games_equal(controller1.game, controller2.game)

    def __check_two_games_equal(self, game1: Game, game2: Game):
        self.assertEqual(game1.even_team_score, game2.even_team_score)
        self.assertEqual(game1.odd_team_score, game2.odd_team_score)
        self.assertEqual(len(game1.rounds), len(game2.rounds))
        for ri in range(len(game1.rounds)):
            r1 = game1.rounds[ri]
            r2 = game2.rounds[ri]
            self.assertEqual(r1.trump, r2.trump)
            self.assertEqual(r1.trump_caller, r2.trump_caller)
            self.assertEqual(len(r1.tricks), len(r2.tricks))
            if len(r1.tricks) == 5:
                for ti in range(5):
                    self.assertEqual(r1.tricks[ti].start_index, r2.tricks[ti].start_index)
                    for ci in range(4):
                        self.assertEqual(r1.tricks[ti].cards[ci], r2.tricks[ti].cards[ci])


if __name__ == '__main__':
    unittest.main()


import unittest
from euchre.serializer import is_game_json_valid, game_to_json, json_to_game
from euchre.data_model import CardDeck, PlayerCards, Round


class TestGameSerializer(unittest.TestCase):

    def test_game_to_json_simple(self):
        cards = CardDeck().deal_cards()
        players = [PlayerCards(i, i, cards[i]) for i in range(4)]
        game = Round(players, cards[4])
        json_game_str = game_to_json(game)
        is_game_json_valid(json_game_str)

    def test_json_to_game_simple(self):
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 11, 5, 10, 25], "dropped_card": null}, ' \
              '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
              '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
              '{"index": 3, "order": 3, "hand": [0, 2, 18, 19, 17], "dropped_card": null}], ' \
              '"deck": [28, 4, 8, 21], "tricks": [], "trump_caller": null, "trump": null}'
        f_round = json_to_game(json_str)
        json_str2 = game_to_json(f_round)
        self.assertEqual(json_str, json_str2)
        is_game_json_valid(json_str2)


if __name__ == '__main__':
    unittest.main()

import unittest
import euchre.valid_moves as vm
from euchre.data_model import FaceCard, Suite, CardDeck, PlayerCards, PartialRound, Round
from euchre.serializer import json_to_game


class TestValidMoves(unittest.TestCase):
    def test_is_trump(self):
        cards = CardDeck().cards
        trump = Suite(0)
        trump_cards = [c for c in cards if vm.is_trump(c, trump)]
        self.assertEqual(len(trump_cards), 7)
        # Check for the left bower
        left_bower = [c for c in trump_cards if c.suite != trump]
        self.assertEqual(len(left_bower), 1)
        self.assertEqual(left_bower[0].face_card, FaceCard.JACK)

    def test_trump_value(self):
        cards = CardDeck().cards
        trump = Suite(0)
        trump_values = [vm.trump_value(c, trump) for c in cards]
        self.assertEqual(set(trump_values), set([i for i in range(8)]), "Incorrect values of trump")
        self.assertEqual(trump_values.count(0), 17)
        for i in range(1, 8):
            self.assertEqual(trump_values.count(i), 1)

    def test_valid_moves_new_game(self):
        cards = CardDeck().deal_cards()
        players = [PlayerCards(i, i, cards[i]) for i in range(4)]
        game = Round(players, cards[4], [], 0, Suite(0))
        p_round = PartialRound.from_round(game, 0)
        valid_cards = vm.valid_trick_moves(p_round)
        self.assertEqual(len(valid_cards), 5)

    def cards_played_by(self):
        raise NotImplementedError

    def test_trick_scoring(self):
        # Test empty trick validated correctly
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 11, 5, 10, 25], "dropped_card": null}, ' \
                   '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
                   '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
                   '{"index": 3, "order": 3, "hand": [0, 2, 18, 19, 17], "dropped_card": null}], ' \
                   '"deck": [28, 4, 8, 21], "tricks": [{"start_index": 0, "cards":[]}], "trump_caller": 0, "trump": 0}'
        json_to_game(json_str)  # Making sure no exception is thrown

        # Exception should be thrown if card outside of players hand is played
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 11, 5, 10, 25], "dropped_card": null}, ' \
                   '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
                   '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
                   '{"index": 3, "order": 3, "hand": [0, 2, 18, 19, 17], "dropped_card": null}], ' \
                   '"deck": [28, 4, 8, 21], "tricks": [{"start_index": 0, "cards":[0]}], "trump_caller": 0, "trump": 0}'
        self.assertRaises(ValueError, json_to_game, json_str)

        # Exception should be thrown if card from players hand is played twice
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 2, 5, 10, 25], "dropped_card": null}, ' \
                   '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
                   '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
                   '{"index": 3, "order": 3, "hand": [0, 11, 18, 19, 17], "dropped_card": null}], ' \
                   '"deck": [28, 4, 8, 21], "tricks": [{"start_index": 0, "cards":[2,29,3,2]}, ' \
                   '{"start_index": 0, "cards":[2]}], "trump_caller": 0, "trump": 0}'
        self.assertRaises(ValueError, json_to_game, json_str)

        # Exception thrown if incorrect player follows a trick playing hand
        json_str = '{"players": [{"index": 0, "order": 0, "hand": [1, 2, 5, 10, 25], "dropped_card": null}, ' \
                   '{"index": 1, "order": 1, "hand": [26, 16, 20, 13, 29], "dropped_card": null}, ' \
                   '{"index": 2, "order": 2, "hand": [9, 27, 24, 12, 3], "dropped_card": null}, ' \
                   '{"index": 3, "order": 3, "hand": [0, 11, 18, 19, 17], "dropped_card": null}], ' \
                   '"deck": [28, 4, 8, 21], "tricks": [{"start_index": 3, "cards":[0,2,29,3]}, ' \
                   '{"start_index": 3, "cards":[2]}], "trump_caller": 0, "trump": 0}'
        self.assertRaises(ValueError, json_to_game, json_str)


if __name__ == '__main__':
    unittest.main()

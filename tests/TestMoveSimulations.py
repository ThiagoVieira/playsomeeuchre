import unittest
from euchre.data_model import FaceCard, Suite, CardDeck, Card, Trick
from euchre.move_simulations import update_possible_cards, possible_cards_in_hand
from euchre.game_controller import GameController
from euchre.players.RandomPlayer import RandomPlayer
from itertools import chain


class TestMoveSimulations(unittest.TestCase):
    def test_possible_cards_in_hand(self):
        cards = [[Card(Suite.DIAMOND, FaceCard.JACK), Card(Suite.DIAMOND, FaceCard.TEN),
                  Card(Suite.DIAMOND, FaceCard.QUEEN), Card(Suite.DIAMOND, FaceCard.ACE),
                  Card(Suite.DIAMOND, FaceCard.KING)],
                 [Card(Suite.CLUB, FaceCard.JACK), Card(Suite.CLUB, FaceCard.TEN),
                  Card(Suite.CLUB, FaceCard.QUEEN), Card(Suite.CLUB, FaceCard.ACE),
                  Card(Suite.CLUB, FaceCard.KING)],
                 [Card(Suite.HEART, FaceCard.JACK), Card(Suite.HEART, FaceCard.TEN),
                  Card(Suite.HEART, FaceCard.QUEEN), Card(Suite.HEART, FaceCard.ACE),
                  Card(Suite.HEART, FaceCard.KING)],
                 [Card(Suite.SPADE, FaceCard.JACK), Card(Suite.SPADE, FaceCard.TEN),
                  Card(Suite.SPADE, FaceCard.QUEEN), Card(Suite.SPADE, FaceCard.ACE),
                  Card(Suite.SPADE, FaceCard.KING)],
                 [Card(Suite.DIAMOND, FaceCard.NINE), Card(Suite.SPADE, FaceCard.NINE),
                  Card(Suite.HEART, FaceCard.NINE), Card(Suite.CLUB, FaceCard.NINE)]]
        possible_cards = possible_cards_in_hand(cards[0], 0, 0, cards[4][0], Suite.DIAMOND, [])
        self.assertTrue(len(possible_cards[0]) == 0, "First player cards should be known")
        self.assertTrue(len([card for card in possible_cards[1] if card.suite == Suite.DIAMOND]) == 0,
                        "Check that the visible players hand is taken out of each persons possible hands")

        tricks = [Trick(2, [Card(Suite.HEART, FaceCard.JACK), Card(Suite.SPADE, FaceCard.JACK),
                            Card(Suite.DIAMOND, FaceCard.JACK), Card(Suite.CLUB, FaceCard.JACK)])]
        possible_cards = possible_cards_in_hand(cards[0], 0, 2, cards[4][0], Suite.SPADE, tricks)
        self.assertTrue(len(possible_cards[0]) == 0, "First player cards should be known")
        self.assertTrue(len([card for card in possible_cards[1] if card.suite == Suite.DIAMOND]) == 0,
                        "Check that the visible players hand is taken out of each persons possible hands")
        self.assertTrue(len([card for card in possible_cards[1] if card.suite == Suite.HEART]) == 0,
                        "Check that if a player could not follow suit card was removed from hand")
        self.assertTrue(len([card for card in possible_cards[4] if card.face_card == FaceCard.JACK]) == 0,
                        "Check that all visible trick cards are removed from possible cards in the deck")

    def test_known_cards_in_hand(self):
        """Idea to test function is to simulate a whole bunch of games and check at each point
        if the set of known cards and possible cards calculated is valid
        """
        whole_deck = sorted([Card(suite, face_card) for face_card in FaceCard for suite in Suite])
        controller = GameController([RandomPlayer(0) for _ in range(4)], CardDeck(0))
        controller.play()
        for g_round in controller.game.rounds:
            if len(g_round.tricks) > 0:
                player_cards = g_round.players_cards[0]
                possible_cards = possible_cards_in_hand(player_cards.hand, player_cards.index, player_cards.order,
                                                        g_round.kitty[0], g_round.trump, g_round.tricks)
                known_cards, possible_cards = update_possible_cards(player_cards.hand, player_cards.index,
                                                                    g_round.tricks, possible_cards)

                self.assertTrue(len(list(chain(*list(possible_cards)))) == 0,
                                "Entire game should be played, possible cards are 0")
                self.assertListEqual(sorted(list(chain(*list(known_cards)))), whole_deck)
                self.assertListEqual(sorted(known_cards[4]), sorted(g_round.kitty))

                for i in range(5):
                    possible_cards = possible_cards_in_hand(player_cards.hand, player_cards.index, player_cards.order
                                                            , g_round.kitty[0], g_round.trump, g_round.tricks)
                    known_cards, possible_cards = update_possible_cards(player_cards.hand, player_cards.index,
                                                                        g_round.tricks, possible_cards)
                    # No repeats in known cards
                    all_known_cards = list(chain(*list(known_cards)))
                    self.assertEqual(len(all_known_cards), len(set(all_known_cards)))
                    # all cards accounted for
                    self.assertEqual(set(list(chain(*list(possible_cards))) + all_known_cards), set(whole_deck))


if __name__ == '__main__':
    unittest.main()

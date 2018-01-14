"""
Logic for an euchre player who performs the most basic strategy above a random move each turn.
"""
from euchre.data_model import Suite, FaceCard, Card, PartialRound
from euchre.players.PlayerInterface import PlayerInterface
import euchre.valid_moves as vm


class BasicPlayer(PlayerInterface):
    """
    Simplest logical euchre player.  Always tries to win a trick with their highest card unless their partner is
    winning the trick, the plays their loewst card.
    """

    def player_type(self) -> str:
        return "Basic Player attempts to win each round, or play lowest card in hand"

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
        valid_cards = vm.valid_trick_moves(p_round)
        if len(valid_cards) == 1:
            return valid_cards[0]

        trick = p_round.tricks[-1]
        lead_suite = trick.cards[0].suite if len(trick.cards) > 0 else None
        valid_card_values = value_cards(valid_cards, p_round.trump, lead_suite)
        valid_card_values.sort(key=lambda x: x[1], reverse=True)  # Sort highest to lowest card value

        if lead_suite is None:
            return valid_card_values[0][0]

        winning_index = vm.trick_winner(trick, p_round.trump)
        winning_card = trick.cards[(winning_index - trick.start_index) % 4]
        winning_card_value = value_cards([winning_card], p_round.trump, lead_suite)[0][1]

        # If your partner is winning the trick, play your lowest card
        if winning_index == (p_round.index - 2) % 4:
            return valid_card_values[-1][0]

        if valid_card_values[0][1] > winning_card_value:
            return valid_card_values[0][0]
        else:
            return valid_card_values[-1][0]


def value_hand(hand: [Card], trump: Suite) -> int:
    """Point score for deciding whether to call trump.  """
    hand_points = sum(vm.trump_value(card, trump) for card in hand)
    hand_points += sum(2 for card in hand if not vm.is_trump(card, trump) and card.face_card == FaceCard.ACE)
    return hand_points


def value_cards(cards: [Card], trump: Suite, lead_suite: Suite) -> (Card, int):
    """Returns a tuple (card, point value) which ranks each card in a hand, point value does not matter"""
    card_values = []
    for card in cards:
        if vm.is_trump(card, trump):
            card_values.append((card, vm.trump_value(card, trump) + 20))
        elif card.suite == lead_suite:
            card_values.append((card, card.face_card.value + 10))
        else:
            card_values.append((card, card.face_card.value))
    return card_values


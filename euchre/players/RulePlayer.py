"""
Logic for an euchre player whose moves with some intermediate knowledge of playing euchre.
"""
import euchre.valid_moves as vm
from euchre.data_model import Suite, FaceCard, Card, PartialRound, PlayerSeat, Trick
from euchre.players.PlayerInterface import PlayerInterface


class RulePlayer(PlayerInterface):
    """
    An intermediate player with some basic logic to play the lowest card to win a trick, sees if the partner is winning
    a trick, and other heuristics above a basic player.

    Arguments: None
    """

    def player_type(self) -> str:
        return "Rule Based Player according to knowledge representation"

    def dealer_pick_up_trump(self, p_round: PartialRound) -> bool:
        if p_round.player_seat is PlayerSeat.DEALER:
            new_hand = p_round.hand + [p_round.flipped_card]
            new_hand.remove(discard_lower_card(new_hand, p_round.flipped_card.suite))
            score = value_bid_hand(new_hand, p_round.flipped_card.suite)
            return score > 3
        elif p_round.player_seat is PlayerSeat.ACROSS_DEALER:
            score = value_bid_hand(p_round.hand, p_round.flipped_card.suite)
            return score > 3
        else:
            score = value_bid_hand(p_round.hand, p_round.flipped_card.suite)
            if p_round.flipped_card.face_card is FaceCard.JACK:
                return score >= 4.5
            else:
                return score >= 3.8

    def dealer_discard_card(self, p_round: PartialRound) -> Card:
        return discard_lower_card(p_round.hand + [p_round.flipped_card], p_round.flipped_card.suite)

    def call_trump(self, p_round: PartialRound) -> Suite or None:
        possible_suites = [s for s in Suite if not p_round.flipped_card.suite]
        max_value, best_suite = 0, None
        for suite in possible_suites:
            hand_value = value_bid_hand(p_round.hand, suite)
            if hand_value > max_value:
                max_value, best_suite = hand_value, suite
        if best_suite is not None and max_value > 3:
            return best_suite
        return None

    def play_card(self, p_round: PartialRound) -> Card:
        moves = vm.valid_trick_moves(p_round)
        if len(moves) == 1:
            return moves[0]

        cards_played = len(p_round.tricks[-1].cards)
        if cards_played == 0:
            return lead_round(moves, p_round.trump, p_round.tricks)
        elif cards_played == 1:
            return play_before_partner(moves, p_round.trump, p_round.tricks[-1])
        else:
            return play_after_partner(moves, p_round.trump, p_round.tricks[-1])


def lead_round(moves: [Card], trump: Suite, tricks: [Trick]) -> Card:
    """Logic of what card to play if player is leading the round"""

    highest_card_in_game = vm.highest_card_left_in_round(tricks, trump)
    trump_cards = [card for card in moves if vm.is_trump(card, trump)]
    off_suite_cards = [card for card in moves if not vm.is_trump(card, trump)]

    if highest_card_in_game is not None and highest_card_in_game in moves:
        return highest_card_in_game
    elif len(trump_cards) == 3 or (len(trump_cards) == 2 and len(tricks) > 2):
        return min(trump_cards, key=lambda c: vm.trump_value(c, trump))
    elif FaceCard.ACE in [c.face_card for c in off_suite_cards]:
        # Could be improved to play Ace of suite with less cards seen in previous tricks or in hand or according
        # to what players have played trump
        return [c for c in off_suite_cards if c.face_card is FaceCard.ACE][0]
    else:
        # Could improve this by checking if trump card would likely be trumped, play off suite card
        # Could improve which off suite card to play by considering Kings, previous cards played
        if len(trump_cards) > 0:
            return max(trump_cards, key=lambda c: vm.trump_value(c, trump))
        else:
            return max(off_suite_cards, key=lambda c: c.face_card)
    # Could add an elif statement for a "Pass the Deal" Strategy


def play_after_partner(moves: [Card], trump: Suite, cur_trick: Trick) -> Card:
    """Logic of what card to play if player is playing after their partner"""

    if vm.is_partner_winning(cur_trick, trump):
        return discard_lower_card(moves, trump)
    else:
        min_winning_card = vm.smallest_winning_card(moves, trump, cur_trick)
        if min_winning_card is not None:
            return min_winning_card
        return discard_lower_card(moves, trump)


def play_before_partner(moves: [Card], trump: Suite, cur_trick: Trick) -> Card:
    """Logic of what card to play if player is playing before their partner"""
    min_winning_card = vm.smallest_winning_card(moves, trump, cur_trick)
    if min_winning_card is not None:
        return min_winning_card
    return discard_lower_card(moves, trump)


def discard_lower_card(hand: [Card], trump: Suite) -> Card:
    """ Discard card to be two suited, unless that card is an Ace, then drop lowest card"""
    trump_cards = [card for card in hand if vm.is_trump(card, trump)]
    off_suite_cards = [card for card in hand if not vm.is_trump(card, trump)]
    off_suites = list(set([c.suite for c in off_suite_cards]))

    if len(off_suite_cards) == 0:
        return min(trump_cards, key=lambda c: vm.trump_value(c, trump))
    elif len(off_suite_cards) == 1:
        return off_suite_cards[0]
    elif len(off_suites) != 2 or len(off_suite_cards) == 2:
        return min(off_suite_cards, key=lambda c: c.face_card.value)
    else:
        min_card_suite_0 = min([c for c in off_suite_cards if c.suite == off_suites[0]],
                               key=lambda c: c.face_card.value)
        min_card_suite_1 = min([c for c in off_suite_cards if c.suite == off_suites[1]],
                               key=lambda c: c.face_card.value)
        return min_card_suite_1 if min_card_suite_0.face_card is FaceCard.ACE else min_card_suite_0


def value_bid_hand(hand: [Card], trump: Suite) -> int:
    """
    Given a hand and a possible trump suite, score how "good" the hand is given the trump
    :param hand:  Players Hand
    :param trump:  Possible Trump Suite
    :return: Point value of hand
    """
    points = 0
    trump_cards = [card for card in hand if vm.is_trump(card, trump)]
    off_suite_cards = [card for card in hand if not vm.is_trump(card, trump)]

    # +1 for off suite ace
    points += sum(1 for card in off_suite_cards if card.face_card is FaceCard.ACE)

    # +1 if two suited
    if len(off_suite_cards) > 0 and len(set([c.suite for c in off_suite_cards])) == 1:
        points += 1

    # value trump based on point system
    for card in trump_cards:
        if card.face_card is FaceCard.JACK:
            if card.suite is trump:         # Its the right
                points += 1
            else:                           # Its the left bower
                points += .8
        elif card.face_card is FaceCard.ACE:
            points += .8
        else:
            points += .5

    return points


"""
Functions for understanding the game state.
"""
from euchre.trump_check import is_trump, trump_value
from euchre.data_model import Suite, FaceCard, Card, Trick, Round, PartialRound, CardSet
from copy import copy


def possible_moves(player_hand: [Card], player_index: int, tricks: [Trick], trump: Suite) -> [Card]:
    """
    Finds a valid moves for a player given his hand, current trump, tricks played, and the player index.
    Note that the player object does not store which cards it has already played, so the cards played by the player
    must be recomputed from the player index and tricks played already.

    :param player_hand: Cards dealt to player.
    :param player_index: Player index.
    :param tricks: Tricks played so far.
    :param trump: Current Trump that is called.
    :return: List of valid card moves the player can choose from
    """

    # This copy and remove is faster than constructing a list of cards not in the cards_played_by function
    cards = copy(player_hand)
    for c in cards_played_by(tricks, player_index):
        cards.remove(c)

    if len(tricks) in [0, 5] or len(tricks[-1].cards) == 0:
        return cards

    trump_cards, non_trump_cards = [], []
    for c in cards:
        if is_trump(c, trump):
            trump_cards.append(c)
        else:
            non_trump_cards.append(c)

    first_card = tricks[-1].cards[0]
    if is_trump(first_card, trump):
        if len(trump_cards) == 0:
            return non_trump_cards
        else:
            return trump_cards
    else:
        same_start_suite_cards = [c for c in non_trump_cards if c.suite == first_card.suite]
        if len(same_start_suite_cards) == 0:
            return cards
        else:
            return same_start_suite_cards


def valid_trick_moves(p_round: PartialRound) -> [Card]:
    """Given a partial game representation, returns a list of valid moves for the player. Used for error checking."""
    if p_round.trump is None:
        raise ValueError("Trump must be called to compute valid moves")
    return possible_moves(p_round.hand, p_round.index, p_round.tricks, p_round.trump)


def cards_played_by(tricks: [Trick], player_index: int) -> [Card]:
    """Given the player index and the number of tricks played so far, returns the cards played by the player"""
    if tricks is None:
        return []
    cards_played = []
    for r in tricks:
        pos_played = (player_index - r.start_index) % 4
        if len(r.cards) > pos_played:
            cards_played.append(r.cards[pos_played])
    return cards_played


def trick_winner(trick: Trick, trump: Suite) -> int:
    """Returns the player index of the winning player so far in the trick """

    win_card = trick.cards[0]
    win_player = trick.start_index

    # Checking for the case the left is played first
    if is_trump(win_card, trump):
        start_suite = trump
    else:
        start_suite = trick.cards[0].suite

    for i in range(1, len(trick.cards)):
        next_card = trick.cards[i]
        if is_trump(next_card, trump):
            if trump_value(next_card, trump) > trump_value(win_card, trump):
                win_card = next_card
                win_player = (trick.start_index + i) % 4
        elif next_card.suite is start_suite:
            if next_card.face_card > win_card.face_card:
                win_card = next_card
                win_player = (trick.start_index + i) % 4

    return win_player


def are_tricks_valid(f_round: Round) -> None:
    """
    Checks if the tricks played so far in the round are valid.  This means that players only played cards in their hand,
    and all cards played followed suite.

    Raises ValueError: If a card was played incorrectly

    :param f_round: Current full round of play
    :return: None
    """

    if f_round.tricks is None or len(f_round.tricks) == 0:
        return
    if f_round.trump is None or f_round.trump_caller is None:
        raise ValueError("Trump must be called to compute valid moves")

    player_played_cards = [[], [], [], []]
    current_player = 3

    for trick in f_round.tricks:
        if trick.start_index != current_player:
            raise ValueError("Current player is not to the left of dealer or winner of last trick")

        for i in range(len(trick.cards)):
            card = trick.cards[i]
            # Check is card in players hand
            if card not in f_round.players_cards[(current_player + i) % 4].hand:
                raise ValueError(str((current_player + i) % 4) + " player played a card not in their hand")
            if card in player_played_cards[(current_player + i) % 4]:
                raise ValueError(str((current_player + i) % 4) + " player played a card in hand twice")
            player_played_cards[(current_player + i) % 4].append(card)

        if len(trick.cards) == 4:
            current_player = trick_winner(trick, f_round.trump)
        else:
            current_player = None


def highest_card_left_in_round(tricks: [Trick], trump: Suite) -> Card or None:
    """
    Given cards played in the trick and trump, compute the highest possible trump card that could still be played.
    If None is returned, all trump cards have been played.
    """

    cards_played = [card for trick in tricks for card in trick.cards]
    card_values_left = set([i for i in range(8)]).difference(set([trump_value(c, trump) for c in cards_played]))
    if len(card_values_left) == 0:
        return None
    highest_value = max(card_values_left)

    if highest_value == 7:
        return Card(trump, FaceCard.JACK)
    elif highest_value == 6:
        return Card(Suite((trump.value + 2) % 4), FaceCard.JACK)
    elif highest_value in [3, 4, 5]:
        return Card(trump, FaceCard(highest_value))
    elif highest_value in [1, 2]:
        return Card(trump, FaceCard(highest_value-1))
    return None


def smallest_winning_card(moves: [Card], trump: Suite, cur_trick: Trick) -> Card or None:
    """
    Finds the smallest value of the card that can win the current state of a trick given a set of moves and trump.
    If the player is not the last player to play, they could still lose the trick.
    """

    lead_suite = trump if is_trump(cur_trick.cards[0], trump) else cur_trick.cards[0].suite

    if lead_suite is trump:
        highest_trump_value = max([trump_value(card, trump) for card in cur_trick.cards])
        winning_moves = [card for card in moves if trump_value(card, trump) > highest_trump_value]
        if len(winning_moves) == 0:
            return None
        else:
            return min(winning_moves, key=lambda c: trump_value(c, trump))
    else:
        lead_suite_moves = [card for card in moves if card.suite == lead_suite]
        trump_moves = [card for card in moves if is_trump(card, trump)]

        if len(lead_suite_moves) > 0:
            return max(lead_suite_moves, key=lambda c: c.face_card.value)
        elif len(trump_moves) > 0:
            return min(trump_moves, key=lambda c: trump_value(c, trump))
        else:
            return None


def is_partner_winning(trick: Trick, trump: Suite) -> bool:
    """
    Checks if the player who played two rounds ago is winning.  Since your partner always plays two cards back,
    knowing this information only requires the current trick and the trump suite.
    """

    if len(trick.cards) <= 1:
        raise ValueError("The partner has not yet played, cannot check if partner is winning")
    trick_index_winner = trick_winner(trick, trump)
    if len(trick.cards) == 2:
        return trick.start_index == trick_index_winner
    else:
        return ((trick.start_index + 1) % 4) == trick_index_winner


def score_round(f_round: Round) -> (int, int):
    """Wrapper function for score tricks given a full round"""
    return score_tricks(f_round.tricks, f_round.trump_caller, f_round.trump)


def score_tricks(tricks: [Trick], trump_caller: int, trump: Suite) -> (int, int):
    """
    Given a completed set of five tricks, the player index of who called trump and the trump suite, computes how many
    points a team scored.
    :return: (int, int) where (Points Scored, Parity of Team who scored the points)
    """

    trump_caller_tricks = 0
    for trick in tricks:
        trick_win_ind = trick_winner(trick, trump)
        if trick_win_ind % 2 == trump_caller % 2:
            trump_caller_tricks += 1
    if trump_caller_tricks == 0:
        return 3, (trump_caller + 1) % 2
    elif trump_caller_tricks in [1, 2]:
        return 2, (trump_caller + 1) % 2
    elif trump_caller_tricks in [3, 4]:
        return 1, trump_caller % 2
    elif trump_caller_tricks == 5:
        return 2, trump_caller % 2



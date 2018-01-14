"""
Functions for understanding the game state.
TODO: COMMENTS!!! and function defintion cleanup
"""
from euchre.trump_check import is_trump
from euchre.data_model import Suite, FaceCard, Card, Trick, PlayerCards
from euchre.valid_moves import cards_played_by
from copy import copy
from itertools import groupby, chain


def possible_cards_in_hand(player_hand: [Card], player_index: int, player_order: int, flipped_card: Card, trump: Suite,
                           tricks: [Trick]) -> [[Card]]:
    """Computes a 5 Card List Tuple of valid cards that could be in each persons hand and in the kitty given the cards
    visible to a given player so far in the game

    Future Improvements could be to cycle over a 24 long boolean array of whether that player has the card for future
    speed improvements."""

    player_cards = [_create_possible_cards() for _ in range(4)]
    deck = _create_possible_cards()

    # The current player knows his hand, and those cards can't be in any other card locations
    # After this point on, a check if card inside hand must be made before every removal from a players hand or the deck
    player_cards[player_index] = []
    for p_ind in range(4):
        if p_ind != player_index:
            for card in player_hand:
                player_cards[p_ind].remove(card)
    for card in player_hand:
        deck.remove(card)
    # Player indexes that represent other people's cards
    player_indexes = [i for i in range(4) if i != player_index]

    # Remove flipped card from everyone but the dealers hand
    if flipped_card.suite == trump:
        # If trump suite is equal to flipped card suite, the card could be in the dealer's hand or discarded
        dealer_index = (player_index + player_order) % 4
        for p_ind in player_indexes:
            if p_ind != dealer_index:
                _conditional_remove(player_cards[p_ind], flipped_card)
    else:
        # Card is in no players hand, was flipped over
        for p_ind in player_indexes:
            _conditional_remove(player_cards[p_ind], flipped_card)

    # Remove cards played so far in the trick from each players hand, assuming a valid trick
    for trick in tricks:
        if trick.start_index is not None and len(trick.cards) > 0:
            for card in trick.cards:
                _conditional_remove(deck, card)
                for p_ind in player_indexes:
                    _conditional_remove(player_cards[p_ind], card)

    # If a player did not follow suit, remove all cards of that suite from hand
    for trick in tricks:
        if trick.start_index is not None and len(trick.cards) > 1:
            lead_card = trick.cards[0]
            cur_index = trick.start_index
            for card in trick.cards[1:]:
                cur_index = (cur_index + 1) % 4
                if cur_index != player_index:
                    if is_trump(lead_card, trump) and not is_trump(card, trump):
                        player_cards[cur_index] = _remove_suite_from_card_list(player_cards[cur_index], trump, trump)
                    elif lead_card.suite != card.suite:
                        player_cards[cur_index] = _remove_suite_from_card_list(player_cards[cur_index], lead_card.suite,
                                                                               trump)

    return player_cards + [deck]


def update_possible_cards(player_hand: [Card], player_index: int, tricks: [Trick], possible_cards: [[Card]]) \
        -> ([[Card]], [[Card]]):
    """Calculates known cards in each players hand as well as possible cards using all information from previous rounds
    """

    player_indexes = [i for i in range(4) if i != player_index]
    known_cards = [[], [], [], [], []]

    known_cards[player_index] = copy(player_hand)
    for p_ind in player_indexes:
        known_cards[p_ind] = cards_played_by(tricks, p_ind)

    known_cards, possible_cards = update_known_cards(known_cards, possible_cards)

    return known_cards, possible_cards


def update_known_cards(known_cards: [[Card]], possible_cards: [[Card]]) -> ([[Card]], [[Card]]):
    known_cards, possible_cards = _remove_known_cards(known_cards, possible_cards)
    while True:
        unique_card_indexes = _compute_unique_card_indexes(possible_cards)
        if len(unique_card_indexes) > 0:
            for card, index in unique_card_indexes:
                known_cards[index].append(card)
                possible_cards[index].remove(card)
            known_cards, possible_cards = _remove_known_cards(known_cards, possible_cards)
        else:
            break
    return known_cards, possible_cards


def possible_deal(known_cards: [[Card]], possible_cards: [[Card]], known_player: PlayerCards, random_gen) \
        -> ([PlayerCards], [Card]):
    while len(list(chain(*known_cards))) < 24:
        # Randomly select a possible card list
        list_indexes = list(range(5))
        random_gen.shuffle(list_indexes)
        list_index = next((i for i in list_indexes if len(possible_cards[i]) > 0), None)
        chosen_card = random_gen.choice(possible_cards[list_index])

        known_cards[list_index].append(chosen_card)
        if (len(known_cards[list_index]) == 5 and list_index < 4) or (len(known_cards[4]) == 4 and list_index == 4):
            possible_cards[list_index] = []
        for possible_card_list in possible_cards:
            _conditional_remove(possible_card_list, chosen_card)

        # Select a possible card, remove from sets
        known_cards, possible_cards = update_known_cards(known_cards, possible_cards)

    player_cards = []
    for i in range(4):
        p_ind = (i + known_player.index) % 4
        p_order = (i + known_player.order) % 4
        player_cards.append(PlayerCards(p_ind, p_order, known_cards[p_ind]))

    return player_cards, known_cards[4]


def _remove_known_cards(known_cards: [[Card]], possible_cards: [[Card]]) -> ([[Card]], [[Card]]):
    """ If the number cards that are possible in a players hand matches the the number of cards left to play,
    you know what is in that players hand.
    """
    known_card_num = -1 # always run once

    while known_card_num != len(list(chain(*known_cards))):
        known_card_num = len(list(chain(*known_cards)))

        # List of player indexes whose entire hand is known from possible cards left that could be in hand
        known_hand_indexes = [p_ind for p_ind in range(4) if (5 - len(known_cards[p_ind])) == len(possible_cards[p_ind])]
        for known_hand_ind in known_hand_indexes:
            if len(known_cards) == 5:
                possible_cards[known_hand_ind] = []
            else:
                for card in possible_cards[known_hand_ind]:
                    known_cards[known_hand_ind].append(card)
                    for card_list in possible_cards:
                        _conditional_remove(card_list, card)

        if len(known_cards[4]) == len(possible_cards[4]):
            for card in possible_cards[4]:
                known_cards[4].append(card)
                for card_list in possible_cards:
                    _conditional_remove(card_list, card)

    return known_cards, possible_cards


def _compute_unique_card_indexes(possible_cards: [[Card]]) -> [[(Card, int)]]:
    """For all possible cards, see if a card only occurs once.  If it occurs once, then that card can only exist in that
    players hand or the deck and can be added to the known list while removed from the possible list
    """
    unique_cards = [key for key, group in groupby(sorted(chain(possible_cards))) if len(list(group)) == 1]
    all_possible_cards = [(card, index) for index in range(5) for card in possible_cards[index]]
    return [card_index for card_index in all_possible_cards if card_index[0] in unique_cards[0]]


def _create_possible_cards():
    return [Card(suite, face_card) for face_card in FaceCard for suite in Suite]


def _conditional_remove(card_list: [Card], card_to_remove: Card):
    """Remove a card from a card list of possible cards if card is in list."""
    if card_to_remove in card_list:
        card_list.remove(card_to_remove)


def _remove_suite_from_card_list(card_list: [Card], suite_to_remove: Suite, trump_suite: Suite):
    if trump_suite == suite_to_remove:
        return list(filter(lambda x: not is_trump(x, trump_suite), card_list))
    else:
        return list(filter(lambda x: x.suite != suite_to_remove or is_trump(x, trump_suite), card_list))


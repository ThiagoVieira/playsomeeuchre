"""
Functions that determine if a card is trump or the rank value of a trump card.

This is the most called function in the game due to the left bower being trump in a given game. To speed up this call,
all possible trump calls are precomputed and saved into a dictionary.

An alternative to looking up trump each time would be to pre-calculate whether a card is trump and its value once trump
has been selected.  This approach was not taken so that reasoning about the data structure card would be easier when
performing logic
"""
from euchre.data_model import Suite, FaceCard, Card


def _trump_dict_key(card: Card, trump: Suite) -> int:
    """Returns a unique card value given a card and a trump value"""
    return (card.value << 2) + trump.value


def _is_trump_calculate(card: Card, trump: Suite) -> bool:
    """Checks if a card is trump, given the integer suite of trump"""
    if card.suite == trump:
        return True
    if card.face_card is FaceCard.JACK and card.suite == (trump.value + 2) % 4:
        return True
    return False


def _create_trump_dict() -> {}:
    """Creates a lookup dictionary of every card and trump combination and whether it is trump or not."""
    trump_dict = {}
    for card in [Card(suite, face_card) for face_card in FaceCard for suite in Suite]:
        for suite in Suite:
            trump_dict[_trump_dict_key(card, suite)] = _is_trump_calculate(card, suite)
    return trump_dict


class _IsTrump(object):
    """
    Calculate all possible checks of whether a card is trump (24*4 keys)
    Which saves about .5 seconds per 1000 simulated euchre games, or about a 20% speed up.
    """
    trump_dictionary = _create_trump_dict()


def is_trump(card: Card, trump: Suite) -> bool:
    return _IsTrump.trump_dictionary[_trump_dict_key(card, trump)]


def trump_value(card: Card, trump: Suite):
    """
    Returns an ordered trump value of the card from 0-7 representing its priority in trump terms.
    7 is the right bower, 1 is a nine of trump and 0 is not trump
    """
    if card.face_card is FaceCard.JACK:
        if card.suite is trump:
            return 7
        elif (card.suite.value + 2) % 4 is trump.value:
            return 6
        else:
            return 0
    elif card.suite is trump:
        if card.face_card is FaceCard.ACE:
            return 5
        elif card.face_card is FaceCard.KING:
            return 4
        elif card.face_card is FaceCard.QUEEN:
            return 3
        elif card.face_card is FaceCard.TEN:
            return 2
        else:
            return 1
    else:
        return 0



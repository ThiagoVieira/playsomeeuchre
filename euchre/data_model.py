"""
Data structures needed to play a game of euchre.

Note that the enumerations for a card Suite and FaceCard significantly slow down playing a game (5-10% of calls) but
make the code easier to read.

Also, NamedTuples could be used for some of the classes that are purely data to speed up creating an instance
and calling its data.

"""
from random import random, Random
from enum import IntEnum, Enum, unique
from copy import copy
from collections import namedtuple


@unique
class Suite(IntEnum):
    """ Card Suite unique enumeration, slows down simulation but makes the code easier to understand."""
    HEART = 0
    SPADE = 1
    DIAMOND = 2
    CLUB = 3


@unique
class FaceCard(IntEnum):
    """ Card Face Value unique enumeration, slows down simulation but makes the code easier to understand. """
    NINE = 0
    TEN = 1
    JACK = 2
    QUEEN = 3
    KING = 4
    ACE = 5


class Card(object):
    """
    Represents a playing card in the game.  Represented by a 5 bit integer.

    Attributes:
        suite: Suite enum.
        face_card: FaceCard enum.
        value: 5 bit int unique card value.  First 3 bits are the face card value, next 2 are the suite.
    """

    def __init__(self, suite: Suite, face_card: FaceCard):
        """ Default constructor takes a Suite and FaceCard enum to create unique card"""
        self.suite = suite
        self.face_card = face_card
        self.value = (suite.value << 3) + face_card.value

    @classmethod
    def with_value(cls, value):
        """Alternative Constructor to create a copy of a card from a given value"""
        return cls(Suite(value >> 3), FaceCard(value % 8))

    def __str__(self):
        return str(self.face_card.name) + " of " + str(self.suite.name)

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __hash__(self):
        return self.value


class CardDeck(object):
    """
    Represents a deck of cards in a game of Euchre.  Automatically shuffles the card upon creation based on a random
    seed given or also chose at random.

    Attribute:
        seed: Integer seed value, provided or randomly generated
        random_generator: random
        cards: list of 24 cards in a euchre deck, shuffled
    """

    def __init__(self, seed: int = None):
        """
        Creates a list of cards in a euchre game and saves a random generator to be used to shuffle the deck
        :param seed: Optional random seed to be used when shuffling the list of cards in the deck
        """
        if seed is None:
            self.seed = random()
        else:
            self.seed = seed
        self.random_generator = Random(self.seed)
        self.cards = [Card(suite, face_card) for face_card in FaceCard for suite in Suite]

    def shuffle_cards(self):
        self.random_generator.shuffle(self.cards)

    def deal_cards(self) -> [[Card]]:
        self.shuffle_cards()
        return [self.cards[0:5], self.cards[5:10], self.cards[10:15], self.cards[15:20], self.cards[20:24]]


CardSet = namedtuple('CardSet', 'Player0 Player1 Player2 Player3 Kitty')
""" Represents a set of cards that each player and the deck current has or a possible cards for each player and deck.
    Attributes: ([Card], [Card], [Card], [Card], [Card]) 
"""


@unique
class PlayerSeat(IntEnum):
    """Seat location of a player in reference to the dealer.  Used to notify user playing where the deal is."""
    DEALER = 0
    RIGHT_OF_DEALER = 1
    ACROSS_DEALER = 2
    LEFT_OF_DEALER = 3


class PlayerCards(object):
    """
    Represents the data a player in a euchre game knows about its own hand.

    Attributes:
        index: a number 0-3, does not change between deals.  Used to tie it to a PlayerAI
        order: number 0-3, 0 represents the dealer, corresponds to the PlayerSeat Enum
        hand: list of 5 cards dealt to this player
        dropped_card: if player is the dealer, this card is only set if the player is the dealer and drops a card
    """

    def __init__(self, index: int, order: int, hand: [Card], dropped_card: Card = None):
        self.index = index
        self.order = order
        self.hand = hand
        self.dropped_card = dropped_card if order == 0 else None


Trick = namedtuple('Trick', 'start_index cards')
""" Represents the current trick in a round of euchre.  The order of the cards matter, with the first card in the list
representing the first card played.

This was changed from a class object with these two attributes to speed up computations slightly

Attributes:
    start_index = 0-3 integer representing the index of the player who started playing this trick
    cards = list of cards representing what was played, first card in this list is the first card played

"""


class Round(object):
    """
     Represents a round of euchre play for a given deal.  It is possible for a completed game to have no tricks played
     as this implies that all players passed on calling trump, no screw the dealer.

    Attributes:
        players_cards: List of player objects and cards dealt to them. Order doesn't matter as each player has an index
        kitty: Cards not dealt to players
        tricks: Cards played each round
        trump_caller: 0-3 digit number, index of player who called trump
        trump: Suite Enum of trump for this game
    """

    def __init__(self, players_cards: [PlayerCards], kitty: [Card], tricks: [Trick] = None, trump_caller: int = None,
                 trump: Suite = None):
        """
        Initializes a data structure to store the current state of a round of euchre.  Players with a dealt hand and
        the cards in the kitty must always be provided, other params are optional and can be updated as the game
        progresses
        """
        self.players_cards = players_cards
        self.kitty = kitty
        self.flipped_card = copy(kitty[0])  # Note, the top of the kitty can change if this card is picked up
        self.tricks = tricks if tricks is not None else []
        self.trump_caller = trump_caller
        self.trump = trump

    @staticmethod
    def copy_tricks(tricks: [Trick]) -> [Trick]:
        """Copies tricks using a list comprehension is 100x faster than using deep copy.

        Remember when copying a structure with a nested list the reference to the list is copied, not the list, unless
        deep copy or the current method is used."""
        return [Trick(tricks[i].start_index, copy(tricks[i].cards)) for i in range(len(tricks))]


class PartialRound(object):
    """ An euchre round object that represents the current state of the round known to a single player.

    Attributes:
        index: Given player index's game state knowledge.
        order: order of play, who is dealer.
        hand: Cards in this players hand.
        dropped_card: If dealer, card dropped if suite was selected.
        tricks: Cards played each round by all players.
        flipped_card: The card that was flipped over.
        trump_caller: 0-3 digit number of player index who called trump, or None if not called yet.
        trump: Suite enumeration that is trump this round, or None if not called yet.
    """

    def __init__(self, player_cards: PlayerCards, tricks: [Trick], flipped_card: Card, trump_caller: int, trump: Suite):
        self.index = player_cards.index
        self.order = player_cards.order
        self.hand = copy(player_cards.hand)
        self.dropped_card = copy(player_cards.dropped_card)
        self.player_seat = PlayerSeat(player_cards.order)
        self.tricks = Round.copy_tricks(tricks)
        self.flipped_card = flipped_card
        self.trump_caller = trump_caller
        self.trump = trump

    @classmethod
    def from_round(cls, f_round: Round, player_index: int):
        """ Creates an object that stores game state information only visible to the given player index

        :param f_round: Full Game State of the round.
        :param player_index: Player index used to decide which game state information is visible to it in the round
        """
        player = next((p for p in f_round.players_cards if p.index == player_index), None)
        return cls(player, f_round.tricks, f_round.flipped_card, f_round.trump_caller, f_round.trump)


@unique
class GameAction(Enum):
    """ Represents the state of a play of a game of euchre.  Assumes rounds are played until a team has 11 points."""
    START_ROUND = 0
    DEAL_ROUND = 1
    DOES_DEALER_PICK_UP = 2
    DISCARD_CARD = 3
    CALL_TRUMP = 4
    PLAY_CARDS = 5
    SCORE_ROUND = 6
    GAME_OVER = 7


class Game(object):
    """
    Game object that represents the state of play for four players until a team has 11 points.

    Attributes:
        card_deck: CardDeck object that is used to shuffle cards in between rounds.  This is important to be able to
            reproduce the hands dealt to each player in a deterministic way.
        rounds: Rounds of play so far.  Last item in list is current round in play.
        current_dealer: Index of player that is the current dealer in the game.
        current_action: Current Game action that is to occur.
        odd_team_score: Points players 1,3 have scored
        even_team_score: Points players 0,2 have scored
    """

    def __init__(self, card_deck: CardDeck = None):
        self.card_deck = card_deck if card_deck is not None else CardDeck()
        self.rounds = []
        self.current_dealer = 0
        self.current_action = GameAction.START_ROUND
        self.odd_team_score = 0
        self.even_team_score = 0




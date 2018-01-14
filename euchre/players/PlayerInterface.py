"""
Interface of functions a euchre player must implement to play a game of euchre given game information
"""
from euchre.data_model import Suite, Card, PartialRound
from abc import ABCMeta, abstractmethod


class PlayerInterface:
    """
    Player Interface to be implemented by all custom logic to play the euchre game.  There are four main functions that
    are needed for the Game Controller, dealer_pick_up_trump, dealer_discard_card, call_trump, play_card.

    ready_to_play and wait_for_user overlap for most calls, just not when the game is starting.  In that case,
    the player is not ready to play yet as they have not seen its hand, but its not waiting for user input.  Once the
    game has started, if the player is ready to play you are not waiting for the user.

    Further Improvements:
        At an added computation cost, could include decorators above each function checking validity of current move
        given the partial information of the round.
    """
    __metaclass__ = ABCMeta

    def ready_to_play(self) -> bool:
        """
        Used by a Round/Game Controller to determine if the player is ready for the next move.  If not, Game/Round
        Controller knows to call out to web player to request next move data. In the case of a non-human player
        defaults to always ready.

        :return: Bool, True if ready, False if not ready
        """
        return True

    def wait_for_user(self) -> bool:
        """
        Used by a Round/Game Controller to determine if the player is waiting for outside input to calculate its next
        move.  In the case of a non-human player defaults to never waiting, always False.

        :return: Bool, True if waiting for user to make a move, False if can continue playing
        """
        return False

    @abstractmethod
    def player_type(self) -> str:
        """
        Function to determine the player logic that implements this interface.

        :return: String explaining the logic behind this players actions.
        """
        raise NotImplementedError

    @abstractmethod
    def dealer_pick_up_trump(self, p_round: PartialRound) -> bool:
        """
        Given the game state available to the player, decide if the dealer should pick up the card, deciding trump.

        :param p_round: Game State observable to player
        :return: True if the dealer picks up card, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def dealer_discard_card(self, p_round: PartialRound) -> Card:
        """
        Only called if the player is the dealer and the dealer or another player wants to pick up the face card. In this
        case the dealer must decide which card to decide from their hand.

        :param p_round: Current Game State observable to player
        :return: Card to be discarded from dealers hand
        """
        raise NotImplementedError

    @abstractmethod
    def call_trump(self, p_round: PartialRound) -> Suite or None:
        """
        Ask player to call trump suite that is not the face_card value.  None if player passes on calling Trump

        :param p_round: Current Game State observable to player
        :return: Trump Suite or None to Pass
        """
        raise NotImplementedError

    @abstractmethod
    def play_card(self, p_round: PartialRound) -> Card:
        """
        Decide on a card to play for the current trick.

        :param p_round: Current Game State observable to player
        :return: A card to be played from the players hand.
        """
        raise NotImplementedError




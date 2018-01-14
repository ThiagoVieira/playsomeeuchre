"""
Logic for An euchre player whose moves are determined from web call (or any other external source).
"""
import euchre.valid_moves as vm
from euchre.data_model import Suite, Card, PartialRound, GameAction
from euchre.players.PlayerInterface import PlayerInterface
from enum import Enum


class WebPlayerState(Enum):
    """Internal State of web player"""
    WAITING_FOR_DATA = 0
    WAITING_FOR_USER = 1
    READY_TO_PLAY = 2


class WebPlayer(PlayerInterface):
    """
    A web player that determines its next moves from an external user and no internal logic.  This is done in the
    game controller by "pausing" the action state if the web player is not ready to play.  In the web player, the first
    time one of the four user actions are called (dealer_pick_up_trump, dealer_discard, call_trump, play_card), valid
    user choices are populated and control returned to the caller.  At this point the controller of the Web Player
    calls set_user_move to update the player state and the next time a user action is called, the user move is used.

    Arguemnts:
        current_move: Current move received from web interface to be played
        game_state: Current Game Action state
        user_choices: Valid choices a human can play on the next round
        player_state: Internal state of the web player.
    """

    def __init__(self):
        self.current_move = None
        self.game_state = None
        self.user_choices = None
        self.player_state = WebPlayerState.WAITING_FOR_DATA

    def set_user_move(self, move):
        self.current_move = self.user_choices[move]
        self.player_state = WebPlayerState.READY_TO_PLAY

    def ready_to_play(self):
        """Override ready_to_play with internal player state"""
        return self.player_state == WebPlayerState.READY_TO_PLAY

    def wait_for_user(self):
        """Override waiting for user with internal player state"""
        return self.player_state == WebPlayerState.WAITING_FOR_USER

    def player_type(self) -> str:
        return "Web Player: plays actions according to online input"

    def dealer_pick_up_trump(self, p_round: PartialRound) -> bool:
        if self.ready_to_play() and self.game_state == GameAction.DOES_DEALER_PICK_UP:
            self.player_state = WebPlayerState.WAITING_FOR_DATA
            return self.current_move

        self.game_state = GameAction.DOES_DEALER_PICK_UP
        self.user_choices = {"Tell Dealer To Pick it up": True, "Pass": False}
        self.player_state = WebPlayerState.WAITING_FOR_USER
        return None

    def dealer_discard_card(self, p_round: PartialRound) -> Card:
        if self.ready_to_play() and self.game_state == GameAction.DISCARD_CARD:
            self.player_state = WebPlayerState.WAITING_FOR_DATA
            return self.current_move

        self.game_state = GameAction.DISCARD_CARD
        self.user_choices = {str(c): c for c in [p_round.flipped_card] + p_round.hand}
        self.player_state = WebPlayerState.WAITING_FOR_USER
        return None

    def call_trump(self, p_round: PartialRound) -> Suite or None:
        if self.ready_to_play() and self.game_state == GameAction.CALL_TRUMP:
            self.player_state = WebPlayerState.WAITING_FOR_DATA
            return self.current_move

        self.game_state = GameAction.CALL_TRUMP
        self.user_choices = {str(s): s for s in Suite if s != p_round.flipped_card.suite}
        self.user_choices['Pass'] = None
        self.player_state = WebPlayerState.WAITING_FOR_USER
        return None

    def play_card(self, p_round: PartialRound) -> Card:
        if self.ready_to_play() and self.game_state == GameAction.PLAY_CARDS:
            self.player_state = WebPlayerState.WAITING_FOR_DATA
            return self.current_move

        self.game_state = GameAction.PLAY_CARDS
        self.user_choices = {str(c): c for c in vm.valid_trick_moves(p_round)}
        self.player_state = WebPlayerState.WAITING_FOR_USER
        return None


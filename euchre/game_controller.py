"""
Classes that contain the logic to play a euchre game.

GameController plays rounds of euchre until a team has 11 points.
RoundController plays a round of euchre consisting of 5 tricks.
"""
import euchre.valid_moves as vm
from euchre.data_model import CardDeck, Game, GameAction, Round, PartialRound, PlayerCards, Trick
from euchre.players.PlayerInterface import PlayerInterface
from euchre.players.FullMonteCarloPlayer import FullMonteCarloPlayer


class GameController(object):
    """
    Controller object that plays a game of euchre given player objects that process moves.  The web player interface was
    added to allow for a break in computing the next move and allowing the GameController object to be pickled and saved
    to disk while waiting for the game to resume with an action from a human player.

    Arguments:
        players: A list of 4 players that implement the PlayerInterface methods to process moves in a euchre game.
            The order of players determines the first round of play and each players index in each round.
        card_deck: A card deck provided to the game controller with a random seed to produce re-creatable games
        web_player: If one player is a web_player, specify this player here to allow for pausing game computation.
        wait_for_web_user: Save the function from the web_player interface to see if the player is ready to play.
        round_controller: Current round being played controller object.
    """

    def __init__(self, players: [PlayerInterface], card_deck: CardDeck = None, web_player: PlayerInterface = None):
        self.players = players
        self.game = Game(card_deck)
        self.web_player = web_player
        self.wait_for_web_user = web_player.wait_for_user if web_player is not None else lambda *_: False
        self.round_controller = None

    def play(self) -> Game:
        """
        Game Logic for playing a euchre until a team has 11 points.  The game is split into game actions that mirror
        actual play, with a new round controller being created and played until a team wins.

        :return: Game object that has been played to completion.
        """

        while self.game.current_action is not GameAction.GAME_OVER and not self.wait_for_web_user():
            if self.game.current_action is GameAction.START_ROUND:
                self.round_controller = RoundController(self.players, self.game.current_dealer, self.game.card_deck)
                self.game.current_action = GameAction.DEAL_ROUND

            elif self.game.current_action is GameAction.DEAL_ROUND:
                self.game.current_action = self.round_controller.deal_new_round()

            elif self.game.current_action is GameAction.DOES_DEALER_PICK_UP:
                self.game.current_action = self.round_controller.dealer_pick_up_card()

            elif self.game.current_action is GameAction.DISCARD_CARD:
                self.game.current_action = self.round_controller.discard_card()

            elif self.game.current_action is GameAction.CALL_TRUMP:
                self.game.current_action = self.round_controller.call_trump()

            elif self.game.current_action is GameAction.PLAY_CARDS:
                self.game.current_action = self.round_controller.play_round()

            elif self.game.current_action is GameAction.SCORE_ROUND:
                # Only score a played game, its possible all players passed and no trump was called.
                if len(self.round_controller.cur_round.tricks) == 5:
                    points, team_parity = vm.score_round(self.round_controller.cur_round)
                    if team_parity == 1:
                        self.game.odd_team_score += points
                    else:
                        self.game.even_team_score += points

                self.game.rounds.append(self.round_controller.cur_round)

                # Check if a team has won or start a new round
                if self.game.odd_team_score >= 10 or self.game.even_team_score >= 10:
                    self.game.current_action = GameAction.GAME_OVER
                else:
                    self.game.current_dealer = (self.game.current_dealer + 1) % 4
                    self.game.current_action = GameAction.START_ROUND

            elif self.game.current_action is GameAction.GAME_OVER:
                pass  # For Completeness of Game Actions
            else:
                raise ValueError("Game Action incorrectly specified")

        return self.game


class RoundController(object):
    """
    Controller object that plays a single round of euchre given a player index and one set of shuffled cards.

    Arguments:
        players: Player AI logic that implements PlayerInterface to decide on next move given game information
        current_dealer: Index of player that is current dealer
        card_deck: Deck of cards being used for game play
        cur_round: Current Round Data object
        web_player_start: Index of web_player in the current round object.  Used to resume play at correct player.
    """

    def __init__(self, players: [PlayerInterface], current_dealer: int, card_deck: CardDeck = None):
        self.players = players
        self.current_dealer = current_dealer
        self.card_deck = card_deck if card_deck is not None else CardDeck()
        self.cur_round = None
        self.web_player_start = 0

    def play(self) -> Round:
        """
        Play option to be used during testing simulations so that each part of game play does not have to be called.
        Game controller calls each of the round actions with this same logic.

        :return: A finished round given the initial players and card deck
        """
        self.deal_new_round()
        if self.dealer_pick_up_card() == GameAction.CALL_TRUMP:
            if self.call_trump() == GameAction.SCORE_ROUND:
                return self.cur_round
        else:
            self.discard_card()
        self.play_round()
        return self.cur_round

    def deal_new_round(self) -> GameAction:
        """Deal hand to each player and create a round game state object.  Initialize any player AI's"""
        cards = self.card_deck.deal_cards()
        players_cards = [PlayerCards(pi, (self.current_dealer + pi) % 4, cards[pi]) for pi in range(4)]
        players_cards.sort(key=lambda x: (3 - x.order) % 4, reverse=True)
        self.cur_round = Round(players_cards, cards[4])
        for player in self.players:
            if type(player) is FullMonteCarloPlayer:
                player.calculate_game_tree(self.cur_round)

        return GameAction.DOES_DEALER_PICK_UP

    def dealer_pick_up_card(self) -> GameAction:
        """
        Ask each player if they want the dealer to pick up the card. If so, record player index and notify dealer.
        If not, move to ask each player to call a trump suite.
        """
        for pi in range(self.web_player_start, 4):
            p = self.cur_round.players_cards[pi]
            player = self.players[p.index]

            if not player.ready_to_play():
                player.dealer_pick_up_trump(PartialRound(self.cur_round, p.index))
                self.web_player_start = pi
                return GameAction.DOES_DEALER_PICK_UP
            else:
                self.web_player_start = 0

            if player.dealer_pick_up_trump(PartialRound.from_round(self.cur_round, p.index)):
                self.cur_round.trump_caller = p.index
                self.cur_round.trump = self.cur_round.flipped_card.suite
                return GameAction.DISCARD_CARD
        return GameAction.CALL_TRUMP

    def discard_card(self):
        """Ask the dealer to discard a card so game play can begin"""
        dealer_hand = next((x for x in self.cur_round.players_cards if x.order == 3), None)
        dealer = self.players[dealer_hand.index]

        if not dealer.ready_to_play():
            dealer.dealer_discard_card(PartialRound.from_round(self.cur_round, dealer_hand.index))
            return GameAction.DISCARD_CARD

        discarded_card = dealer.dealer_discard_card(PartialRound.from_round(self.cur_round, dealer_hand.index))
        dealer_hand.dropped_card = discarded_card
        if discarded_card in dealer_hand.hand:
            dealer_hand.hand.remove(discarded_card)
            dealer_hand.hand.append(self.cur_round.flipped_card)
            self.cur_round.kitty[0] = discarded_card # To keep integrity of the data structure
        return GameAction.PLAY_CARDS

    def call_trump(self) -> GameAction:
        """
        If face card was not picked, ask each player if they want to call trump.  If so, return player index and
        called trump.  If not, the round is finished with no winner, the dealer moves, and a new set of cards is dealt.
        """
        for pi in range(self.web_player_start, 4):
            p = self.cur_round.players_cards[pi]
            player = self.players[p.index]

            if not player.ready_to_play():
                player.call_trump(PartialRound.from_round(self.cur_round, p.index))
                self.web_player_start = pi
                return GameAction.CALL_TRUMP
            else:
                self.web_player_start = 0

            trump = player.call_trump(PartialRound.from_round(self.cur_round, p.index))
            if trump is not None:
                self.cur_round.trump_caller = p.index
                self.cur_round.trump = trump
                return GameAction.PLAY_CARDS
        return GameAction.SCORE_ROUND

    def play_round(self) -> GameAction:
        """Play all five tricks of the game once trump is called."""
        while len(self.cur_round.tricks) < 5:
            if len(self.cur_round.tricks) == 0:
                start_index = next((x.index for x in self.cur_round.players_cards if x.order == 0), None)
                self.cur_round.tricks.append(Trick(start_index, []))

            trick = self.cur_round.tricks[-1]
            if len(trick.cards) == 4:
                start_index = vm.trick_winner(self.cur_round.tricks[-1], self.cur_round.trump)
                trick = Trick(start_index, [])
                self.cur_round.tricks.append(trick)

            for i in range(self.web_player_start, 4):
                player = self.players[(i + trick.start_index) % 4]

                if not player.ready_to_play():
                    player.play_card(PartialRound.from_round(self.cur_round, (i + trick.start_index) % 4))
                    self.web_player_start = i
                    return GameAction.PLAY_CARDS
                else:
                    self.web_player_start = 0
                trick.cards.append(player.play_card(PartialRound.from_round(self.cur_round, (i + trick.start_index) % 4)))

        return GameAction.SCORE_ROUND






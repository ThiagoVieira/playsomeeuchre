"""
Logic for an euchre player whose moves are entered through the command line.
"""
from euchre.data_model import Suite, Card, PartialRound, Trick
from euchre.players.PlayerInterface import PlayerInterface
import euchre.valid_moves as vm


class CommandLinePlayer(PlayerInterface):
    """ A player that reaches out to the terminal for user input on what card to play next """

    def player_type(self) -> str:
        return "CommandLine Player"

    def dealer_pick_up_trump(self, p_round: PartialRound) -> bool:
        choices = "Press [0] for dealer to pick up trump, Press [1] to pass"
        current_state = [self.__current_position(p_round.order),
                         self.__current_hand(p_round.hand),
                         self.__flipped_card(p_round.flipped_card)]
        print("\n".join(current_state))
        valid_inputs = ['0', '1']
        user_choice = self.__get_user_input(p_round, valid_inputs, choices)
        return user_choice == '0'

    def dealer_discard_card(self, p_round: PartialRound) -> Card:
        cards = p_round.hand + [p_round.flipped_card]
        choices = "Please discard a card" + "\n"\
            .join(["Press [" + str(i) + "] to drop card: " + str(cards[i]) for i in range(6)])
        current_state = [self.__current_position(p_round.order)]
        print("\n".join(current_state))
        valid_inputs = ['0', '1', '2', '3', '4', '5']
        user_choice = self.__get_user_input(p_round, valid_inputs, choices)
        return cards[int(user_choice)]

    def call_trump(self, p_round: PartialRound) -> Suite or None:
        suites = [s for s in Suite if s != p_round.flipped_card.suite]
        choices = "You have the option of calling trump. \nPress [0] to pass \n" + \
                  "\n".join(["Press [" + str(i+1) + "] for suite " + str(suites[i]) for i in range(3)])
        current_state = [self.__current_position(p_round.order),
                         self.__current_hand(p_round.hand),
                         self.__flipped_card(p_round.flipped_card)]
        print("\n".join(current_state))
        valid_inputs = ['0', '1', '2', '3']
        user_choice = self.__get_user_input(p_round, valid_inputs, choices)
        return suites[int(user_choice)-1]

    def play_card(self, p_round: PartialRound) -> Card:
        cards = vm.valid_trick_moves(p_round)
        choices = "Choose a card to play \n" + \
            "\n".join(["Press [" + str(i) + "] for " + str(cards[i]) for i in range(len(cards))])
        current_state = [self.__trump_status(p_round),
                         self.__trick_status(p_round.tricks[-1])]
        if len(p_round.tricks) > 1:
            current_state.insert(0, self.__trick_result(p_round.tricks[-2], p_round.index))
        print("\n".join(current_state))
        valid_inputs = [str(i) for i in range(len(cards))]
        user_choice = self.__get_user_input(p_round, valid_inputs, choices)
        return cards[int(user_choice)]

    def __get_user_input(self, p_round: PartialRound, valid_inputs: [str], choices: str) -> str:
        """Checks for valid user input and allows for the user to print out a summary
        of the current game state"""
        user_prompt = choices + " \nPress [r] to print out current game state. \n"
        user_input = None
        while user_input not in valid_inputs:
            user_input = input(user_prompt)
            if user_input == 'r':
                print(self.__print_current_state(p_round))
        return user_input

    @staticmethod
    def __trump_status(p_round: PartialRound) -> str:
        players = ["You", "Player to the right", "Your teammate", "Player to the left"]
        player = players[(p_round.trump_caller - p_round.index) % 4]
        return "Trump is " + str(p_round.trump.name) + " called by " + player

    @staticmethod
    def __trick_result(trick: Trick, index: int) -> str:
        player_options = ["first", "second", "third", "last"]
        player = "You are the " + player_options[(index - trick.start_index) % 4] + " player in this trick."
        return player + "\n Cards played: " + ", ".join([str(c) for c in trick.cards])

    @staticmethod
    def __trick_status(trick: Trick) -> str:
        player_options = ["first", "second", "third", "last"]
        player = "You are the " + player_options[len(trick.cards)] + " player."
        if len(trick.cards) > 0:
            return player + "\n Cards played so far: " + ", ".join([str(c) for c in trick.cards])
        else:
            return player

    @staticmethod
    def __flipped_card(card: Card) -> str:
        return "Card for dealer is: " + str(card)

    @staticmethod
    def __current_hand(cards: [Card]) -> str:
        return "Your hand is: " + ", ".join([str(c) for c in cards])

    @staticmethod
    def __current_position(index: int) -> str:
        seats = ["the dealer", "right of the dealer", "across from the dealer", "left of the dealer"]
        return "You are " + seats[index]

    @staticmethod
    def __print_current_state(p_round: PartialRound) -> str:
        """Returns a string with all the information regarding the game up to the current point
        for the current player"""
        info_str = [CommandLinePlayer.__current_position(p_round.index),
                    CommandLinePlayer.__current_hand(p_round.hand),
                    CommandLinePlayer.__flipped_card(p_round.flipped_card)]
        if p_round.trump is not None:
            info_str.append(CommandLinePlayer.__trump_status(p_round))
        for trick in p_round.tricks[0:-1]:
            info_str.append(CommandLinePlayer.__trick_result(trick, p_round.index))
        if len(p_round.tricks) > 0:
            info_str.append(CommandLinePlayer.__trump_status(p_round))

        return "\n".join(info_str)


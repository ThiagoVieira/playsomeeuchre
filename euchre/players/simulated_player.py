#TODO Top level comment for this file and all Functions
import euchre.valid_moves as vm
from euchre.players.RandomPlayer import RandomPlayer
from euchre.data_model import Card, PartialRound
from euchre.players.BasicPlayer import BasicPlayer
from euchre.players.RulePlayer import RulePlayer
from enum import Enum
from collections import namedtuple


SimulatedPlayer = namedtuple('SimulatedPlayer', 'index logic_depth_0 logic_depth_1 logic_depth_2')
"""SimulatedPlayer named tuple is passed to function create_simulated_players to specify AI logic 

There are no logic_depths_3 or 4, at this point MIN_MAX logic is always used to evaluate last two options.

:param index: is the index of the player in the game
:param logic_depth_0: PlayerSimulationLogic Enum to describe action on first round of play
:param logic_depth_1: PlayerSimulationLogic Enum to describe action on second round of play
:param logic_depth_2: PlayerSimulationLogic Enum to describe action on third round of play
"""

_PlayerLogic = namedtuple('_PlayerLogic', 'index logic_depth_0 logic_depth_1 logic_depth_2')
"""_PlayerLogic named tuple contains references to functions to compute player moves at each logic depth  

There are no logic_depths_3 or 4, at this point MIN_MAX logic is always used to evaluate last two options.

:param index: is the index of the player in the game
:param logic_depth_0: Represents a function of form play_card(p_round: PartialRound) to compute a player move
:param logic_depth_1: Represents a function of form play_card(p_round: PartialRound) to compute a player move
:param logic_depth_2: Represents a function of form play_card(p_round: PartialRound) to compute a player move
"""


class PlayerSimulationLogic(Enum):
    """Player Logic to use when expanding a game tree node in a game tree simulation.

    MIN_MAX logic expands all possible valid moves a given round while other logic just chooses option.
    """
    MIN_MAX = 0
    RANDOM = 1
    BASIC = 2
    RULE = 3


def min_max_logic(p_round: PartialRound) -> [Card]:
    """MIN MAX player logic that given current visible round information, returns all valid card moves list"""
    return vm.possible_moves(p_round.hand, p_round.index, p_round.tricks, p_round.trump)


def create_simulated_players(specified_players: [SimulatedPlayer], random_seed: int = None) -> [_PlayerLogic]:
    """Create simulated players to run a game tree analysis on for best possible move

    Given the specified player logic types, creates the player types that embody the logic for that move. Once the
    logic/functions are created, returns an internal representation of the logic as a list of _PlayerLogic types

    :param specified_players: a list of 4 player logic types to run the simulations on
    :param random_seed: optional random seed if a random player is used to be able to recreate simulations
    :return: [_PlayerLogic] class to that represents logic to be played at each game tree step
    """
    random_player = RandomPlayer(random_seed)
    basic_player = BasicPlayer()
    rule_player = RulePlayer()

    def random_logic(p_round: PartialRound): return [random_player.play_card(p_round)]

    def basic_logic(p_round: PartialRound): return [basic_player.play_card(p_round)]

    def rule_logic(p_round: PartialRound): return [rule_player.play_card(p_round)]

    def get_player(player_sim_logic: PlayerSimulationLogic):
        if player_sim_logic is PlayerSimulationLogic.MIN_MAX:
            return min_max_logic
        elif player_sim_logic is PlayerSimulationLogic.RANDOM:
            return random_logic
        elif player_sim_logic is PlayerSimulationLogic.BASIC:
            return basic_logic
        elif player_sim_logic is PlayerSimulationLogic.RULE:
            return rule_logic
        else:
            return None

    logic_players = []
    for specified_player in specified_players:
        logic_players.append(_PlayerLogic(specified_player.index,
                                          get_player(specified_player.logic_depth_0),
                                          get_player(specified_player.logic_depth_1),
                                          get_player(specified_player.logic_depth_2)))
    return logic_players


def create_min_max_players() -> [SimulatedPlayer]:
    specified_players = []
    for index in range(4):
        specified_players.append(SimulatedPlayer(index, PlayerSimulationLogic.MIN_MAX, PlayerSimulationLogic.MIN_MAX,
                                                 PlayerSimulationLogic.MIN_MAX))
    return specified_players


def create_random_players() -> [SimulatedPlayer]:
    specified_players = []
    for index in range(4):
        specified_players.append(SimulatedPlayer(index, PlayerSimulationLogic.RANDOM, PlayerSimulationLogic.RANDOM,
                                                 PlayerSimulationLogic.RANDOM))
    return specified_players


def create_simple_min_max_players(min_max_index: int) -> [SimulatedPlayer]:
    specified_players = []
    for index in range(4):
        if min_max_index == index:
            specified_players.append(SimulatedPlayer(index, PlayerSimulationLogic.MIN_MAX,
                                                     PlayerSimulationLogic.MIN_MAX, PlayerSimulationLogic.MIN_MAX))

        else:
            specified_players.append(SimulatedPlayer(index, PlayerSimulationLogic.RULE, PlayerSimulationLogic.RULE,
                                                     PlayerSimulationLogic.RULE))
    return specified_players


def get_player_logic(sim_player_logic: [_PlayerLogic], player_index: int, trick_depth: int):
    if trick_depth > 2:
        return min_max_logic
    else:
        simulated_player = next((player for player in sim_player_logic if player.index == player_index), None)
        if trick_depth == 0:
            return simulated_player.logic_depth_0
        elif trick_depth == 1:
            return simulated_player.logic_depth_1
        else:
            return simulated_player.logic_depth_2



"""
Improvements:
    Alpha-Beta Pruning
         Alpha beta pruning with imperfect information is hard and computational expensive to calculate.  At each round,
         the known information about other players cards from previous hands could be calculated and possible moves
         that are certain to work/fail could be chosen.  A probability distribution of opponents cards could also be
         inferred and used to improve the "best guess" at each point.

    Imperfect Information Set Game Tree
        Could implement the algorithm by Peter I Cowling to improve speed up and search
"""
import euchre.valid_moves as vm
import random
from euchre.data_model import Suite, Card, PlayerCards, Trick,  PartialRound, Round
from euchre.players.simulated_player import SimulatedPlayer, get_player_logic, create_simulated_players
from euchre.move_simulations import update_possible_cards, possible_cards_in_hand, possible_deal

"""The below approach of using a dictionary instead of a GameNode class as initially specifieed below is due to
performance enhancements.  Using this dictionary structure saves 50% time as there is half as many dictionary lookups
to access one of these base elements.  Tuples are slightly faster, but non-mutable for creating the children links.

class GameNode(object):
    def __init__(self, player_index: int, parent_node, child_nodes, current_tricks: [Trick]):
        self.player_index = player_index
        self.parent_node = parent_node
        self.child_nodes = child_nodes
        self.current_tricks = current_tricks
"""
NODE_PLAYER_INDEX = "NODE_PLAYER_INDEX"
NODE_PARENT_NODE = "NODE_PARENT_NODE"
NODE_CHILDREN = "NODE_CHILDREN"
NODE_CURRENT_TRICKS = "NODE_CURRENT_TRICKS"
NODE_BEST_CHILD = "NODE_BEST_CHILD"
NODE_BEST_SCORE = "NODE_BEST_SCORE"

def create_game_node(player_index: int, parent_node: dict, children: [dict], current_tricks: [Trick]):
    """Creates a node in a simulated game tree of the current state of the game in terms of the cards played, current
    player turn, and parent/child nodes accessible from this node"""
    return {NODE_PLAYER_INDEX: player_index, NODE_PARENT_NODE: parent_node, NODE_CHILDREN: children,
            NODE_CURRENT_TRICKS: current_tricks}


#TODO Rename mc_sim vs GameTreeSImulation object to be clear
class GameTreeSimulation(object):

    def __init__(self, players_cards: [PlayerCards], simulated_players: [SimulatedPlayer], deck: [Card],
                 trump_caller: int, trump: Suite, tricks: [Trick] = None, random_seed: int = 0):
        self.players_cards = players_cards
        self.players_logic = create_simulated_players(simulated_players, random_seed)
        self.deck = deck
        self.trump_caller = trump_caller
        self.trump = trump
        self.tricks = tricks if tricks is not None else [Trick(0, [])]
        self.game_tree = None

    def simulate(self):
        """ Creates a game tree of a simulated game given the initial euchre game parameters by expanding each possible
          decision point starting for the current trick passed in."""
        self.game_tree = create_game_node(self.tricks[-1].start_index, None, [], self.tricks)
        self.expand_node(self.game_tree)
        return self.game_tree

    def create_partial_round(self, tricks: [Trick], player_index: int) -> PartialRound:
        """Creates a partial round data object to be given to a player logic to calculate the next move"""
        player = next((p for p in self.players_cards if p.index == player_index), None)
        return PartialRound(player, tricks, self.deck[0], self.trump_caller, self.trump)

    def expand_node(self, parent_node: dict):
        """Calculates all moves given a player logic for the current point in the game tree and then expands children
        nodes"""

        if len(parent_node[NODE_CURRENT_TRICKS]) == 4 and len(parent_node[NODE_CURRENT_TRICKS][-1].cards) == 4:
            # Set child nodes to None to indicate the a game tree ending.  Empty list indicates computations pending.
            parent_node[NODE_CHILDREN] = None
            return
        elif len(parent_node[NODE_CURRENT_TRICKS]) == 1 and len(parent_node[NODE_CURRENT_TRICKS][0].cards) == 0:
            # Default behavior for an empty trick set is to simulate all possible cards in had as a next move
            next_player_index = parent_node[NODE_PLAYER_INDEX]
        elif len(parent_node[NODE_CURRENT_TRICKS][-1].cards) == 4:
            # Create a new trick and set the player index to the previous trick's winner
            next_player_index = vm.trick_winner(parent_node[NODE_CURRENT_TRICKS][-1], self.trump)
            parent_node[NODE_CURRENT_TRICKS].append(Trick(next_player_index, []))
        else:
            # Move to the next player
            next_player_index = (parent_node[NODE_PLAYER_INDEX] + 1) % 4

        # Use simulation logic to calculate next valid branching move for the given player in game tree
        sim_logic = get_player_logic(self.players_logic, next_player_index, len(parent_node[NODE_CURRENT_TRICKS]))
        cards = sim_logic(self.create_partial_round(parent_node[NODE_CURRENT_TRICKS], next_player_index))

        # For each possible child move, copy trick data and append new move to create child game node.
        # Append expanded (calculated) game node to parent
        for card in cards:
            current_tricks = Round.copy_tricks(parent_node[NODE_CURRENT_TRICKS])
            current_tricks[-1].cards.append(card)
            child_node = create_game_node(next_player_index, parent_node, [], current_tricks)
            self.expand_node(child_node)
            parent_node[NODE_CHILDREN].append(child_node)

    #TODO Function that searches gameNodeTree, marks each node with best possible move and current point value of best move
    #TODO Helper Method to extract best move from solved min max Tree once calculated for unit testing, PERFECT INFO


class MC_Simulation(object):

    def __init__(self, player_cards: PlayerCards, simulated_players: [SimulatedPlayer], flipped_card: Card,
                 trump_caller: int, trump: Suite, tricks: [Trick] = None, num_simulations: int = 10,
                 random_seed: int = 0):
        self.player_cards = player_cards
        self.simulated_players = simulated_players
        self.flipped_card = flipped_card
        self.trump_caller = trump_caller
        self.trump = trump
        self.tricks = tricks if tricks is not None else [Trick(0, [])]
        self.num_simulations = num_simulations
        self.random_seed = random_seed
        self.random_gen = random.Random(random_seed)
        self.game_trees = []

    def simulate(self):
        possible_cards = possible_cards_in_hand(self.player_cards.hand, self.player_cards.index,
                                                self.player_cards.order, self.flipped_card, self.trump,
                                                self.tricks)
        known_cards, possible_cards = update_possible_cards(self.player_cards.hand, self.player_cards.index,
                                                            self.tricks, possible_cards)
        #TODO Look into making this multithreaded
        for i in range(self.num_simulations):
            player_cards, deck = possible_deal(known_cards, possible_cards, self.player_cards, self.random_gen)
            game_tree_sim = GameTreeSimulation(player_cards, self.simulated_players, deck, self.trump_caller,
                                               self.trump, self.tricks, self.random_seed)
            game_node = game_tree_sim.simulate()
            # Added about two seconds... for 10 sims.  Base line is 3.3 for 10 sims, 5.5 with scoring..
            score_game_node(game_node, self.trump_caller, self.trump)
            self.game_trees.append(game_node)


def score_game_node(game_node: dict, trump_caller: int, trump: Suite):
    """Compute the best child_move to make given the parent node.  Recursive calls here."""

    if game_node[NODE_CHILDREN] is None:
        # Indicates this is the end of the game node
        trick_score, team_parity = vm.score_tricks(game_node[NODE_CURRENT_TRICKS], trump_caller, trump)
        did_node_win = team_parity == game_node[NODE_PLAYER_INDEX] % 2
        game_node[NODE_BEST_SCORE] = trick_score * (1 if did_node_win else -1)
        game_node[NODE_BEST_CHILD] = None
    else:
        for child_node in game_node[NODE_CHILDREN]:
            score_game_node(child_node, trump_caller, trump)

        child_node_parity = game_node[NODE_CHILDREN][0][NODE_PLAYER_INDEX] % 2
        node_parity = game_node[NODE_PLAYER_INDEX] % 2

        if child_node_parity == node_parity:
            best_node = max(game_node[NODE_CHILDREN], key=lambda node: node[NODE_BEST_SCORE])
        else:
            best_node = min(game_node[NODE_CHILDREN], key=lambda node: node[NODE_BEST_SCORE])

        game_node[NODE_BEST_CHILD] = best_node
        game_node[NODE_BEST_SCORE] = best_node[NODE_BEST_SCORE] * (1 if (child_node_parity == node_parity) else -1)


class GameTreeStatistics(object):

    def __init__(self, game_tree: dict):
        self.game_tree = game_tree
        self.tree_depth = 0
        self.num_nodes = 0
        self.avg_branch_1 = 0
        self.avg_branch_2 = 0
        self.avg_branch_3 = 0
        self.avg_branch_4 = 0
        self.calculate_stats()

    def calculate_stats(self):
        parent_node = self.game_tree
        while parent_node[NODE_CHILDREN] is not None:
            self.tree_depth += 1
            parent_node = parent_node[NODE_CHILDREN][0]

        def count_child_nodes(game_node: dict) -> int:
            if game_node[NODE_CHILDREN] is None:
                return 0
            else:
                return len(game_node[NODE_CHILDREN]) + sum([count_child_nodes(node) for node in game_node[NODE_CHILDREN]])
        self.num_nodes = count_child_nodes(self.game_tree) + 1




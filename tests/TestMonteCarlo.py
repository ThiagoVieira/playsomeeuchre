import unittest
import pickle

from euchre.data_model import Suite, CardDeck, PlayerCards
from euchre.game_simulations import MC_Simulation, GameTreeSimulation, GameTreeStatistics
from euchre.players.simulated_player import create_min_max_players, create_random_players


class TestMonteCarlo(unittest.TestCase):

    def test_min_max_sim(self):
        cards = CardDeck(0).deal_cards()
        players_cards = [PlayerCards(i, i, cards[i]) for i in range(4)]
        game_sim = GameTreeSimulation(players_cards, create_min_max_players(), cards[4], 0, Suite.DIAMOND)
        game_tree = game_sim.simulate()
        game_stats = GameTreeStatistics(game_tree)

        self.assertEqual(game_stats.tree_depth, 16)
        self.assertEqual(game_stats.num_nodes, 24367)

    def test_random_simulation_reproducible(self):
        cards = CardDeck(0).deal_cards()
        players_cards = [PlayerCards(i, i, cards[i]) for i in range(4)]

        mc_sim_1 = GameTreeSimulation(players_cards, create_random_players(), cards[4], 0, Suite.CLUB)
        mc_tree_1 = mc_sim_1.simulate()
        mc_pickle_1 = pickle.dumps(mc_tree_1)

        mc_sim_2 = GameTreeSimulation(players_cards, create_random_players(), cards[4], 0, Suite.CLUB)
        mc_tree_2 = mc_sim_2.simulate()
        mc_pickle_2 = pickle.dumps(mc_tree_2)

        self.assertEqual(mc_pickle_1, mc_pickle_2)

    def test_mc_sim(self):
        cards = CardDeck(0).deal_cards()
        players_cards = [PlayerCards(i, i, cards[i]) for i in range(4)]
        flipped_card = cards[4][0]
        mc_sim = MC_Simulation(players_cards[0], create_random_players(), flipped_card, 0, flipped_card.suite, None)
        mc_sim.simulate()


    def test_minmax_vs_minmax_game_trees(self):
        #TODO Test that the minmax player against 4 other minmax players produce the outcome you would expect
        print("")

    def test_minmax_vs_rule_player_simulation(self):
        #TODO test a non MINMAX Sim player
        print("")





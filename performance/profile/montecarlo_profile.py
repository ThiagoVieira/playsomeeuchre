import cProfile

from euchre.data_model import CardDeck, PlayerCards, Suite
from euchre.game_simulations import GameTreeSimulation

# Profile MonteCarlo Call, takes about 70 seconds on a full min max
cards = CardDeck().deal_cards()
players = [PlayerCards(i, i, cards[i]) for i in range(4)]
mc_sim = GameTreeSimulation(players, cards, 0, Suite.DIAMOND)
cProfile.run('mc_sim.simulate()')





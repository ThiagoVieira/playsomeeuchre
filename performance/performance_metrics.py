from euchre.players.RandomPlayer import RandomPlayer
from euchre.players.BasicPlayer import BasicPlayer
from euchre.players.RulePlayer import RulePlayer
from performance.test_performance_util import EuchreSim, print_results


# Simple test of 3 types of players
starting_players = [[RandomPlayer(i) for i in range(4)], [BasicPlayer() for _ in range(4)],
                    [RulePlayer() for _ in range(4)], [BasicPlayer()] + [RandomPlayer(i) for i in range(3)],
                    [RulePlayer()] + [RandomPlayer(i) for i in range(3)]]
for players in starting_players:
    euchre_sim = EuchreSim(players, 1000)
    results = euchre_sim.simulate()
    print(players[0].player_type())
    print("Sim Time: " + str(euchre_sim.sim_time))
    print("Score Time: " + str(euchre_sim.score_time))
    print_results(results)



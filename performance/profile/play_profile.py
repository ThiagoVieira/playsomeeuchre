import cProfile
from performance.test_performance_util import EuchreSim
from euchre.players.RandomPlayer import RandomPlayer


# Print out time to run 1000 games with random players
euchre_sim = EuchreSim([RandomPlayer(i) for i in range(4)])
results = euchre_sim.simulate()
print("Sim Time: " + str(euchre_sim.sim_time))

# Actual profile of 1000 games
cProfile.run('EuchreSim([RandomPlayer(i) for i in range(4)]).simulate()')


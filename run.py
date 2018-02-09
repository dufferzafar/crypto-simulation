
from simulation import Simulator


if __name__ == '__main__':

    # TODO: Take input from user
    n = 10
    z = 0.3

    sim = Simulator(n, z)

    print(sim.nodes)

    # c = sim.run(until=4)

    # print("%d events were run." % c)

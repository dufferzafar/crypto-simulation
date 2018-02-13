from simulation import Simulator


if __name__ == '__main__':

    # TODO: Take input from user
    n = 10
    z = 0.3

    sim = Simulator(n, z)

    sim.run(until)
    sim.dump_node_chains()
    sim.dump_network()

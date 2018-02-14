import argparse

from simulation import Simulator

# Build a CLI argument parser
P = argparse.ArgumentParser(
    description='Discrete-event simulator for P2P Cryptocurrency Network.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

P.add_argument('n', type=int, default=10,
               help='Number of nodes')

P.add_argument('z', type=float, default=0.4,
               help='Fraction of slow nodes')

P.add_argument('tm', type=float, default=5,
               help='Mean transaction interarrival time')

P.add_argument('bm', type=float, default=10,
               # metavar="Tk",
               help='Mean block interarrival time')

P.add_argument('--until', type=int, default=1000,
               help='Maximum number of events to run')

P.add_argument('-q', action="store_true",
               help='Do not print event log')

if __name__ == '__main__':

    args = P.parse_args()

    # If not given as a fraction, then assume percentage
    if args.z > 1:
        args.z /= 100

    sim = Simulator(args.n, args.z, args.tm, args.bm)

    sim.remove_graphs()

    sim.run(args.until, args.q)
    sim.dump_network()
    sim.dump_node_chains()

    sim.convert_graphs()

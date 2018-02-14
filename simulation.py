"""
This module implements the simulation.

Using nodes, blocks, and events.
"""

# Python's stdlib
import os
import random

from queue import PriorityQueue
from collections import Counter

# Our custom code
import events as EV
from node import Node

# Change this to configure where the output graphs are stored
OUT_DIR = "output"

if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR)


class Simulator(object):

    def __init__(self, n, z, tm, bm):

        # Total number of nodes
        self.n = n

        # Fraction of slow nodes
        self.z = z

        # Mean transaction interarrival time
        self.tm = tm

        # Mean block interarrival time
        self.bm = bm

        # The event queue prioritised by the scheduled time of the event
        self.events = PriorityQueue()

        # All nodes in the simulation
        self.nodes = self.create_nodes(n, z)

        # Randomize peers of each node!
        self.set_random_peers()

        # TODO: Use itertools.count for these
        # Block id
        self.block_id = 1

        # Transaction id
        self.trans_id = 1

        # Current time of the simulation
        self.curr_time = 0

        # Set propagation delays between each pair of nodes
        self.prop_delay = [
            # From assignment:
            # Pij can be chosen from a uniform distribution between 10ms and 500ms
            [random.uniform(10, 501) / 1000 for _ in range(0, n)]
            for _ in range(0, n)
        ]

        # Add some intial events
        self.seed_events_queue()

    def transaction_delay(self):
        """Use an exponential distribution for interarrival between transactions."""
        return random.expovariate(1 / self.tm)

    def block_delay(self):
        """Use an exponential distribution for interarrival between blocks."""
        return random.expovariate(1 / self.bm)

    def create_nodes(self, n, z):
        """Create n nodes z% of which are slow."""

        slow_nodes = [
            Node(node_id=i, initial_coins=random.randrange(11, 31), is_fast=False)
            for i in range(0, int(n * z))
        ]

        fast_nodes = [
            Node(node_id=i, initial_coins=random.randrange(11, 31), is_fast=True)
            for i in range(int(n * z), n)
        ]

        return slow_nodes + fast_nodes

    def set_random_peers(self):
        """
        Set random peers of each node.

        Care needs to be taken to ensure that the resulting graph is connected, so
        that every node can send messages to every other node.
        """

        for me in self.nodes:
            # This ensures that network graph remains connected
            # But this doesn't consider all possible connected graphs!
            num_peers = random.randint(1 + self.n // 2, self.n - 1)

            all_but_me = list(set(self.nodes) - set([me]))

            me.peers = random.sample(all_but_me, num_peers)

    def seed_events_queue(self):
        """Seed the events queue with BlockGenerate & TransactionGenerate events."""

        for node in self.nodes:
            self.events.put(EV.BlockGenerate(
                node.id, node.id, 0, self.block_delay()
            ))

            self.events.put(EV.TransactionGenerate(
                node.id, node.id, 0, self.transaction_delay()
            ))

    def run(self, until=100, quiet=False):
        """Run all events until some max number of events."""

        events = Counter()
        ev_count = 1

        if not quiet:
            print("     N |     t      |     Event")
            print("       |            |")

        while ev_count <= until:

            ev = self.events.get()
            self.curr_time = ev.run_at

            if not quiet:
                print("%6d | %.8f | %s" % (ev_count, self.curr_time, ev))

            ev.run(self)

            ev_count += 1

            # Keep track of which type of events run
            ev_type = type(ev).__name__
            events[ev_type] += 1

        print("\n\nCounts of events run: \n")
        for e, c in sorted(events.items()):
            print("{:<19} | {}".format(e, c))
        print("{:^19} | {}".format("Total", ev_count - 1))

    def latency(self, a, b, msg_type):
        """Return latency between nodes a & b."""

        i, j = self.nodes.index(a), self.nodes.index(b)

        # Propagation delays p_ij chosen at start of simulation
        p = self.prop_delay[i][j]

        # for a msg of only 1 transaction: assume that |m| = 0
        if msg_type == "transaction":
            m = 0
        # for a msg of a block: assume that |m| = 1 MB (8 × 10**6 b)
        elif msg_type == "block":
            m = 8 * (10 ** 6)
        else:
            raise ValueError("msg_type")

        # c_ij is set to 100 Mbps if both i and j are fast
        if a.is_fast and b.is_fast:
            c = 100 * (10 ** 6)
        # and 5 Mbps if either is slow
        else:
            c = 5 * (10 ** 6)

        # mean of d_ij is set equal to 96kbit/c_ij
        d_mean = 12 * 8 * (10 ** 3) / c

        # d_ij is the queuing delay on the path
        # randomly chosen from an exponential distribution with above mean
        d = random.expovariate(1 / d_mean)

        # latency is of the form p_ij + |m|/c_ij + d_ij
        return (p + m / c + d)

    def dump_node_chains(self, pruned=False):
        """
        Save the blockchain tree of every node to .dot files.

        Outputs are graphs in graphviz format:
        https://en.wikipedia.org/wiki/DOT_(graph_description_language)

        To convert them to png run:
        """

        for node in self.nodes:

            node_type = "fast" if node.is_fast else "slow"
            prune = "_pruned" if pruned else ""

            file = "%d_%s%s.dot" % (node.id, node_type, prune)

            with open(os.path.join(OUT_DIR, file), "w+") as fh:

                # Graphviz header format
                # TODO: Stylish graph nodes etc. (lookup gdot documentation)
                fh.write("digraph G { \n")
                fh.write('rankdir="LR";\n\n')

                # Draw edges of the blockchain tree
                for block in node.blocks.values():

                    if block.prev_block_id != -1:
                        edge = "\t%d -> %d\n" % (block.prev_block_id, block.id)

                        fh.write(edge)

                    # else:
                    #     edge = "%d\n" % block.id

                # Close the graph
                fh.write("\n}")

    def dump_network(self):
        """
        Save the network connections to a .dot file.
        """

        file = "network.dot"
        with open(os.path.join(OUT_DIR, file), "w+") as fh:

            fh.write("graph G { \n\n")

            seen = set()

            for node in self.nodes:
                for peer in node.peers:

                    # No self-loops
                    if node.id == peer.id:
                        continue

                    # Only draw an edge once
                    edge = (node.id, peer.id)
                    if edge not in seen:

                        # We've seen both edges a->b & b->a
                        seen.add(edge)
                        seen.add(edge[::-1])

                        fh.write("\t%d -- %d\n" % edge)

            fh.write("\n}")

    def prune_node_chains(self):
        """
        Remove all blocks except the longest chain.
        """

        for node in self.nodes:
            node.blocks = {b.id: b for b in node.longest_chain()}

    def convert_graphs(self):
        """
        Convert all .dot files to .png files.
        """

        # TODO: Replace with glob.glob
        for fn in os.listdir(OUT_DIR):

            if fn.endswith(".dot"):

                fn = os.path.join(OUT_DIR, fn)

                graph = fn[:-4] + ".png"
                cmd = "dot -Tpng %s -o %s" % (fn, graph)

                # TODO: Replace with subprocess.call
                os.system(cmd)

    def remove_graphs(self):
        """
        Remove all existing graph files.
        """

        for fn in os.listdir(OUT_DIR):
            if fn.endswith(".dot") or fn.endswith(".png"):
                os.remove(os.path.join(OUT_DIR, fn))

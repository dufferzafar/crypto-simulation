"""
This module implements the simulation.

Using nodes, blocks, and events.
"""

# Python's stdlib
import os
import random

from queue import PriorityQueue

# Our custom code
import events as EV
from node import Node

# Change this to configure where the output graphs are stored
OUT_DIR = "output"

if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR)


class Simulator(object):

    def __init__(self, n, z):

        # Total number of nodes
        self.n = n

        # Fraction of nodes that are slow
        self.z = z

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

        # TODO: Rename to blk_rate
        # TODO: Add similar for txn_rate
        # Lambda value
        self.lmbd = 10

        # Set propagation delays between each pair of nodes
        self.prop_delay = [
            # From assignment:
            # Pij can be chosen from a uniform distribution between 10ms and 500ms
            [random.uniform(10, 501) / 1000 for _ in range(0, n)]
            for _ in range(0, n)
        ]

        # Add some intial events
        self.seed_events_queue()

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
        """Set random peers of each node."""

        # Care needs to be taken to ensure that the resulting graph is connected
        # So every node can send messages to every other node
        # self.peers = random.sample(all_nodes, k) ?

        # TODO: Ensure that this creates a fully connected graph
        for i in range(self.n):
            count = random.randint(1 + self.n // 2, self.n - 1)

            for j in range(count):
                adj = random.randint(0, self.n - 1)

                # Create symmetric links
                if adj not in self.nodes[i].peers:
                    self.nodes[i].peers.append(adj)

                if i not in self.nodes[adj].peers:
                    self.nodes[adj].peers.append(i)

    def seed_events_queue(self):
        """Seed the events queue with BlockGenerate & TransactionGenerate events."""

        for node in self.nodes:
            t = random.expovariate(self.lmbd)

            blk_gen = EV.BlockGenerate(
                node.id,
                node.id,
                0,
                t
            )

            self.events.put(blk_gen)

            trns_gen = EV.TransactionGenerate(
                node.id,
                node.id,
                0,
                t
            )

            self.events.put(trns_gen)

    def run(self, until=100):
        """Run all events until some max number of events."""

        ev_count = 0

        while ev_count <= until:

            ev = self.events.get()

            print("t=%f | " % self.curr_time, type(ev))
            ev.run(self)

            self.curr_time = ev.run_at

            ev_count += 1

        # TODO: Print stats on types of events run
        # print("Total %d events were run." % ev_count)

    def latency(self, a, b, msg_size_mb=0):
        """Return latency between nodes a & b."""

        i, j = self.nodes.index(a), self.nodes.index(b)
        # i = -1
        # j = -1
        # for x in range(self.n):
        #     if self.nodes[x].id == a:
        #         i = x
        #     if self.nodes[x].id == b:
        #         j = b

        # Propagation delays p_ij chosen at start of simulation
        p = self.prop_delay[i][j]

        # TODO: Deal with varying msg_size_mb!
        # for a msg of only 1 transaction: assume that |m| = 0
        # for a msg of a block: assume that |m| = 1 MB (8 × 10**6 b)
        m = msg_size_mb * 8 * (10 ** 6)

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

    def dump_node_chains(self):
        """
        Save the tree of blockchain of ever node.

        Outputs are graphs in graphviz format:
        https://en.wikipedia.org/wiki/DOT_(graph_description_language)

        To convert them to png run:
        """

        for node in self.nodes:

            file = "%d_%s.dot" % (node.id,
                                  "fast" if node.is_fast else "slow")

            with open(os.path.join(OUT_DIR, file), "w+") as fh:

                # Graphviz header format
                # TODO: Stylish graph nodes etc. (lookup gdot documentation)
                fh.write("digraph G { \n\n")

                # Draw edges of the blockchain tree
                for block in node.blocks:

                    if block.prev_block_id != -1:
                        edge = "\t%d -> %d\n" % (block.prev_block_id, block.id)
                        fh.write(edge)
                    # else:
                    #     edge = "%d\n" % block.id

                # Close the graph
                fh.write("\n}")

                # TODO: See if creation times need to be dumped?
                # for block in node.blocks:
                #     line = str(block.id) + ":" + str(block.created_at) + "\n"
                #     fh.write(line)

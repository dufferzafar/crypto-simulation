from queue import PriorityQueue
import random

from node import Node


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

        # Block id
        self.block_id = 1;

        # Transaction id
        self.trans_id = 1;

        # TODO: Set random peers of each node
        # Care needs to be taken to ensure that the resulting graph is connected
        # So every node can send messages to every other node

        #@ankit
        adjmat = [[0 for x in range(n)] for y in range(n)]
        for i in range(n):
            count = randint(n/2,n-1)
            for j in range(count):
                adj = randint(0,n-1)
                if adj not in nodes[i].peers:
                    nodes[i].peers.append(adj)
                if i not in nodes[adj].peers:
                    nodes[adj].peers.append(i)

        # Set propagation delays between each pair of nodes
        self.prop_delay = [
            # From assignment:
            # Pij can be chosen from a uniform distribution between 10ms and 500ms
            [random.uniform(10, 501) / 1000 for _ in range(0, n)]
            for _ in range(0, n)
        ]

        # TODO: Seed the events queue with BlockGenerate & TransactionGenerate events
        #@ankit
        for i in range(n):
            lmbd = nodes[i].lmbd;
            t = math.log(1-random.uniform(0,1))/(-lmbd)
            nextEvent = BlockGenerate(nodes[i].id,nodes[i].id,0,t)
            events.append(nextEvent)

        for i in range(n):
            lmbd = nodes[i].lmbd;
            t = math.log(1-random.uniform(0,1))/(-lmbd)
            nextEvent = TransactionGenerate(nodes[i].id,nodes[i].id,0,t)
            events.append(nextEvent)
        # Current time of the simulation
        self.curr_time = 0

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

    def run(self, until):
        """Run all events until some time."""

        ev_count = 0

        while self.curr_time <= until:

            ev = self.events.get()
            ev.run(self)

            self.curr_time = ev.run_at
            ev_count += 1

        return ev_count

    def latency(self, a, b, msg_size_mb=0):
        """Return latency between nodes a & b."""

        i, j = self.nodes.index(a), self.nodes.index(b)

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
    # @ Avinash 
    # function which create files of the particular simulation


    def printblockchain(self):

        for node in self.nodes:
            fh = open("../output/"+str(node.id)+str(node.is_fast)+".txt","w+")
            for block in node.blocks:
                if x.prev_block_id != -1:
                    line = str(block.prev_block_id)+"->"+str(block.block_id)+"\n"
                    fh.write(line)

            fh.write("\n")
            for block in node.blocks:
                line = str(block.block_id)+":"+str(block.created_at)
                fh.write(line)
            fh.close()

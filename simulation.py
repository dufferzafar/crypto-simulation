from queue import PriorityQueue
from random import randrange

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

        # TODO: Set random peers of each node
        # Care needs to be taken to ensure that the resulting graph is connected
        # So every node can send messages to every other node

        # TODO: Set propagation delays between each pair of nodes

        # TODO: Seed the events queue with BlockGenerate & TransactionGenerate events

        # Current time of the simulation
        self.curr_time = 0

    def create_nodes(self, n, z):
        """Create n nodes z% of which are slow."""

        slow_nodes = [
            Node(node_id=i, initial_coins=randrange(1, 10), is_fast=False)
            for i in range(0, int(n * z))
        ]

        fast_nodes = [
            Node(node_id=i, initial_coins=randrange(1, 10), is_fast=True)
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


if __name__ == '__main__':

    # TODO: Take input from user

    sim = Simulator(10, 0.7)
    c = sim.run(until=4)

    print("%d events were run." % c)

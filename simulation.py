from queue import PriorityQueue


class Simulator(object):

    def __init__(self, n, z):

        # Total number of nodes
        self.n = n

        # Fraction of nodes that are fast
        self.z = z

        # The event queue prioritised by the scheduled time of the event
        self.events = PriorityQueue()

        # All nodes in the simulation
        # TODO: Populate nodes with random initial coins and fast/slow type
        self.nodes = []

        # Current time of the simulation
        self.curr_time = 0

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


class Node(object):

    def __init__(self, node_id, initial_coins, is_fast):
        self.id = node_id
        self.coins = initial_coins

        self.is_fast = is_fast

        # NOTE: What is this for?
        self.receivedStamps = []

        # Stores references to other node objects
        self.peers = []

        # TODO: Each node should have a random number of peers connected
        # import random
        # self.peers = random.sample(all_nodes, k)

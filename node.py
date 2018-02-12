
from block import Block


class Node(object):

    def __init__(self, node_id, initial_coins, is_fast):
        self.id = node_id
        self.coins = initial_coins

        self.is_fast = is_fast

        # NOTE: What is this for?
        self.receivedStamps = []

        # List of this node's neighbours
        self.peers = []

        # List of all blocks this node has seen
        # (can be thought of as a tree using prev_block attribute of a block)
        self.blocks = [

            # Each node begins with a genesis block
            Block(block_id=0, created_at=0.0, creator_id=self.id, prev_block_id=-1,leng=0)

        ]

        # List of transactions this node has seen
        # NOTE: Not really sure if this is really required
        self.transactions = []

        # TODO: Each node should have a random number of peers connected
        # import random
        # self.peers = random.sample(all_nodes, k)

    def __repr__(self):
        r = (self.id, self.coins, ("fast" if self.is_fast else "slow"))
        return "<Node %d:, coins=%d, %s>" % r

    def get(self,blk_id):
        for x in self.blocks:
            if x.id == blk_id:
                return x

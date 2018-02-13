
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

        # Dict of all blocks this node has seen
        # (can be thought of as a tree using prev_block attribute of a block)
        self.blocks = {

            # Each node begins with a genesis block
            0: Block(block_id=0, created_at=0.0, creator_id=self.id,
                     prev_block_id=-1, leng=0)

        }

        # List of transactions this node has seen
        self.transactions = []

    def __repr__(self):
        r = (self.id, self.coins, ("fast" if self.is_fast else "slow"))
        return "<Node %d:, coins=%d, %s>" % r

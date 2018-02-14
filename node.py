
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
                     prev_block_id=-1, chain_len=0)

        }

        # Dict of transactions this node has seen
        self.transactions = {}

    def __repr__(self):
        r = (self.id, self.coins, ("fast" if self.is_fast else "slow"))
        return "<Node %d:, coins=%d, %s>" % r

    def longest_chain(self):
        """
        Return the blocks of the longest chain.
        """

        chain = []

        # Alternative way? https://stackoverflow.com/a/4233482/2043048
        # by_time = sorted(me.blocks.values(), key=lambda b: b.created_at)
        # longest_blk = sorted(by_time, key=lambda b: b.chain_len)

        # Find the block ending with the longest chain
        longest_bk = self.blocks[0]
        for bk in self.blocks.values():

            # Use block creation time to break ties in case of equal length
            if ((len(bk) > len(longest_bk)) or ((len(bk) == len(longest_bk)) and
                                                (bk.created_at < longest_bk.created_at))):
                longest_bk = bk

        # Now find all the blocks in this chain
        bk = longest_bk

        # I hate while True loops but alas, python doesn't have do-while!
        while True:

            chain.append(bk)

            # Chain ends at Genesis block which have id 0
            if bk.id == 0:
                break

            # Move backwards
            bk = self.blocks[bk.prev_block_id]

        return chain

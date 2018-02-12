
class Block(object):

    def __init__(self, block_id, created_at, creator_id, prev_block_id,leng):
        super(Block, self).__init__()

        # TODO: Should this be passed from outside or auto-incremented by us?
        self.id = block_id
        self.created_at = created_at

        # Node that created this block
        self.creator_id = creator_id

        # This link helps create a chain of blocks
        self.prev_block_id = prev_block_id

        # Contains a dict of Transactions
        #self.transactions = {}
        self.transactions = []

        # Length of the chain this block is part of
        self.len = leng;
    def __repr__(self):
        r = (self.id, self.prev_block_id)
        return "<Block %d: prev=%d>" % r


class Transaction(object):

    def __init__(self, trans_id, from_id, to_id, coins):
        super(Transaction, self).__init__()

        self.id = trans_id
        self.from_id = from_id
        self.to_id = to_id
        self.coins = coins

    def __repr__(self):
        r = (self.id, self.from_id, self.to_id, self.coins)
        return "<Trans %d: from=%d, to=%d, coins=%d>" % r

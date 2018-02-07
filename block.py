
class Block(object):

    def __init__(self, block_id, created_at, creator_id, prev_block_id):
        super(Block, self).__init__()

        # TODO: Should this be passed from outside or auto-incremented by us?
        self.id = block_id
        self.created_at = created_at

        # Node that created this block
        self.creator_id = creator_id

        # This link helps create a chain of blocks
        self.prev_block_id = prev_block_id

        # Contains a dict of Transactions
        self.transactions = {}


class Transaction(object):

    def __init__(self, trans_id, from_id, to_id, amount):
        super(Block, self).__init__()

        self.trans_id = trans_id
        self.from_id = from_id
        self.to_id = to_id
        self.amount = amount

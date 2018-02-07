
from block import Block, Transaction


class Event(object):

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(Block, self).__init__()

        # Node this event will happen on
        self.node_id = node_id

        # Node that created this event
        self.creator_id = creator_id

        # Time this event was created
        self.created_at = created_at

        # Time this event will be run at
        self.run_at = run_at

    def __lt__(self, other):
        """Allow sorting of events by their scheduled time."""
        return self.run_at < other.run_at


class TransactionGenerate(Event):

    def __init__(self, **kwargs):
        super(self).__init__(**kwargs)

    def run(sim):

        # Find a random receiver who will receive the coins in the transaction
        # Generate a random amount not greater than current node's balance
        # Update the coins of both sender & receiver
        # Add transaction to current node's transaction list

        # Create next transaction events for this node
        # Create next transaction events for neighbours

        raise NotImplementedError


class TransactionReceive(Event):

    def __init__(self, transaction, **kwargs):
        super(self).__init__(**kwargs)

        self.transaction = transaction

    def run(sim):

        # Check if this node has already seen this transaction before
        # If not, then add it to it's list
        # And generate TransactionReceive events for all its neighbours

        raise NotImplementedError


class BlockGenerate(Event):

    def __init__(self, **kwargs):
        super(self).__init__(**kwargs)

    def run(sim):
        raise NotImplementedError


class BlockReceive(Event):

    def __init__(self, block, **kwargs):
        super(self).__init__(**kwargs)

        self.block = block

    def run(sim):
        raise NotImplementedError

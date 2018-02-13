"""
Implements the four kinds of events that can happen in the simulation.

TransactionGenerate, TransactionReceive, BlockGenerate, BlockReceive
"""

from block import Block, Transaction
import random


class Event(object):

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(Event, self).__init__()

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

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(TransactionGenerate, self).__init__(
            node_id, creator_id, created_at, run_at
        )

    def __repr__(self):
        return "T Gen: on=%d" % self.node_id

    def run(self, sim):
        # The node that this event is running on
        me = sim.nodes[self.node_id]

        # Generate a random amount not greater than current node's balance
        trans_amt = me.coins * random.uniform(0, 1)

        # Find a random receiver who will receive the coins in the transaction
        all_but_me = list(set(sim.nodes) - set([me]))
        receiver = random.choice(all_but_me)

        # Update the coins of both sender & receiver
        me.coins -= trans_amt
        receiver.coins += trans_amt

        # Add transaction to current node's transaction list
        new_trans = Transaction(
            sim.trans_id,
            me.id,
            receiver.id,
            trans_amt
        )

        sim.trans_id += 1
        me.transactions.append(new_trans)

        # Create a next transaction event for this node
        # TODO: Create a separate function in sim for transaction_delay
        t = random.expovariate(sim.lmbd)
        sim.events.put(TransactionGenerate(
            me.id,
            me.id,
            self.run_at,
            self.run_at + t
        ))

        # Create next transaction events for neighbours
        for peer_id in me.peers:
            t = sim.latency(me, sim.nodes[peer_id], msg_type="transaction")

            sim.events.put(TransactionReceive(
                new_trans,
                peer_id,
                me.id,
                self.run_at,
                self.run_at + t
            ))


class TransactionReceive(Event):

    def __init__(self, transaction, node_id, creator_id, created_at, run_at):
        super(TransactionReceive, self).__init__(
            node_id, creator_id, created_at, run_at
        )

        # The transaction that was received
        self.transaction = transaction

    def __repr__(self):
        return "T Rcv: on=%d | %s" % (self.node_id, repr(self.transaction))

    def run(self, sim):
        # The node that this event is running on
        me = sim.nodes[self.node_id]
        tx = self.transaction

        # Check if this node has already seen this transaction before
        if tx.id in me.transactions:
            return

        # If not, then add it to it's list
        me.transactions.append(tx)

        # And generate TransactionReceive events for all its neighbours
        for peer_id in me.peers:

            t = sim.latency(me, sim.nodes[peer_id], msg_type="transaction")
            sim.events.put(TransactionReceive(
                tx,
                peer_id,
                me.id,
                self.run_at,
                self.run_at + t
            ))


class BlockGenerate(Event):

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(BlockGenerate, self).__init__(
            node_id, creator_id, created_at, run_at
        )

    def __repr__(self):
        return "B Gen: on=%d" % self.node_id

    def run(self, sim):
        # Hi, this is me!
        me = sim.nodes[self.node_id]

        # TODO: Learn what this is!
        flag = False
        for x in me.receivedStamps:
            if x > self.run_at:
                flag = True

        if not flag:
            leng = -1
            blk = None

            # Find the block ending with the longest chain
            for x in me.blocks:
                if x.len > leng:
                    leng = x.len
                    blk = x
                    # break

            # TODO: 0 - Remove all
            # Always keep all transactions
            # but only add those to a block that are not already part of the longest chain
            # will nee a copy of the list

            # Traverse the longest chain and remove all transactions that
            # have been logged in it
            for x in me.transactions:
                prevblk = blk

                # Genesis blocks have id 0
                while (prevblk.id != 0):

                    if x in prevblk.transactions:
                        if x in me.transactions:
                            me.transactions.remove(x)

                    prevblk = me.get(prevblk.prev_block_id)

            # Generate a new block
            newblk = Block(
                sim.block_id,
                self.run_at,
                me.id,
                blk.id,
                leng + 1
            )
            sim.block_id += 1
            newblk.transactions.extend(me.transactions)

            # Add the block to my chain
            me.blocks.append(newblk)

            # And give me that sweet sweet mining reward!
            me.coins += 50

            # Generate BlockReceive events for all my peers
            for peer_id in me.peers:

                # Except who created the thing!
                if peer_id != newblk.creator_id:
                    t = sim.latency(me, sim.nodes[peer_id], msg_type="block")

                    sim.events.put(BlockReceive(
                        newblk,
                        peer_id,
                        me.id,
                        self.run_at,
                        self.run_at + t
                    ))


class BlockReceive(Event):

    def __init__(self, block, node_id, creator_id, created_at, run_at):
        super(BlockReceive, self).__init__(
            node_id, creator_id, created_at, run_at
        )

        # The block we've received
        self.block = block

    def __repr__(self):
        return "B Rcv: on=%d | %s" % (self.node_id, repr(self.block))

    def run(self, sim):
        # The node that this event is running on
        me = sim.nodes[self.node_id]

        # Check if this node has already seen this block before
        if self.block.id in me.blocks:
            return

        # Find previous block to the one that we've just received
        blk = None
        for x in me.blocks:
            if x.id == self.block.prev_block_id:
                blk = x
                break

        # TODO: Why would I not have received the previous block?
        if blk is None:
            return

        # Make a copy of the block to increase the length
        newblk = Block(
            self.block.id,
            self.block.created_at,
            self.block.creator_id,
            blk.id,
            self.block.len
        )
        newblk.len += 1

        # Add the block to my chain
        me.blocks.append(newblk)
        me.receivedStamps.append(newblk.created_at)

        # Generate BlockReceive events for all my peers
        for peer_id in me.peers:

            # Except for who created it
            if peer_id != self.block.creator_id:

                t = sim.latency(me, sim.nodes[peer_id], msg_type="block")

                sim.events.put(BlockReceive(
                    self.block,
                    peer_id,
                    me.id,
                    self.run_at,
                    self.run_at + t
                ))

        # TODO: Do we need a schedule time value to be passed as well?
        # Create a new block generation event for me
        t = random.expovariate(sim.lmbd)
        sim.events.put(BlockGenerate(
            me.id,
            me.id,
            self.run_at,
            self.run_at + t
        ))

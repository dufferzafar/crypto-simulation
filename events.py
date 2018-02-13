
from block import Block, Transaction
import random
import math


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

    def run(self, sim):
        # all_but_me = set(sim.nodes) - set([sim.nodes[self.node_id]]);
        # TODO: random.choice(all_but_me)

        # Find a random receiver who will receive the coins in the transaction
        toid = -1
        while(toid == sim.nodes[self.node_id].id):
            toid = random.randint(0, sim.n - 1)

        # Generate a random amount not greater than current node's balance
        factor = random.uniform(0, 1)
        transAmt = sim.nodes[self.node_id].coins * factor

        # Update the coins of both sender & receiver
        sim.nodes[self.node_id].coins -= transAmt
        sim.nodes[toid].coins += transAmt

        # Add transaction to current node's transaction list
        newTrans = Transaction(
            sim.trans_id,
            sim.nodes[self.node_id].id,
            toid,
            transAmt
        )

        sim.trans_id += 1
        sim.nodes[self.node_id].transactions.append(newTrans)

        # Create a next transaction event for this node
        lmbd = sim.lmbd

        # TODO: Create a separate function in sim for transaction_delay
        t = math.log(1 - random.uniform(0, 1)) / (-lmbd)

        sim.events.put(TransactionGenerate(
            sim.nodes[self.node_id].id,
            sim.nodes[self.node_id].id,
            self.run_at,
            self.run_at + t
        ))

        # Create next transaction events for neighbours
        for peer_id in sim.nodes[self.node_id].peers:
            t = sim.latency(sim.nodes[self.node_id], sim.nodes[peer_id], 1)

            sim.events.put(TransactionReceive(
                newTrans,
                peer_id,
                sim.nodes[self.node_id].id,
                self.run_at,
                self.run_at + t
            ))


class TransactionReceive(Event):

    def __init__(self, transaction, node_id, creator_id, created_at, run_at):
        super(TransactionReceive, self).__init__(
            node_id, creator_id, created_at, run_at
        )

        self.transaction = transaction

    def run(self, sim):
        # Check if this node has already seen this transaction before
        if self.transaction.id in sim.nodes[self.node_id].transactions:
            return

        # If not, then add it to it's list
        sim.nodes[self.node_id].transactions.append(self.transaction)

        # And generate TransactionReceive events for all its neighbours
        for peer_id in sim.nodes[self.node_id].peers:

            # TODO: Pass msg type to latency
            t = sim.latency(sim.nodes[self.node_id], sim.nodes[peer_id], 1)

            sim.events.put(TransactionReceive(
                self.transaction,
                peer_id,
                sim.nodes[self.node_id].id,
                self.run_at,
                self.run_at + t
            ))


class BlockGenerate(Event):

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(BlockGenerate, self).__init__(
            node_id, creator_id, created_at, run_at
        )

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
                    t = sim.latency(
                        me,
                        sim.nodes[peer_id],
                        1
                    )
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

    def run(self, sim):
        flag = False
        for x in sim.nodes[self.node_id].blocks:
            if x.id == self.block.id:
                flag = True
                break

        if not flag:
            blk = None
            for x in sim.nodes[self.node_id].blocks:
                if x.id == self.block.prev_block_id:
                    blk = x
                    break

            # To break the loop if previous block does not exist in the current block chain why????
            if blk is None:
                return

            newblk = Block(self.block.id, self.block.created_at,
                           self.block.creator_id, blk.id, self.block.len)
            newblk.len += 1
            sim.nodes[self.node_id].blocks.append(newblk)
            sim.nodes[self.node_id].receivedStamps.append(newblk.created_at)

            for peer_id in sim.nodes[self.node_id].peers:
                if peer_id != self.block.creator_id:
                    t = sim.latency(
                        sim.nodes[self.node_id],
                        sim.nodes[peer_id],
                        1
                    )

                    nextEvent = BlockReceive(
                        self.block,
                        peer_id,
                        sim.nodes[self.node_id].id,
                        self.run_at,
                        self.run_at + t
                    )
                    sim.events.put(nextEvent)

            # Do we need a schedule time value to be passed as well.
            lmbd = sim.lmbd

            t = math.log(1 - random.uniform(0, 1)) / (-lmbd)
            nextEvent = BlockGenerate(
                sim.nodes[self.node_id].id,
                sim.nodes[self.node_id].id,
                self.run_at,
                self.run_at + t
            )
            sim.events.put(nextEvent)

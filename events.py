
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
        t = math.log(1 - random.uniform(0, 1)) / (-lmbd)

        nextEvent = TransactionGenerate(
            sim.nodes[self.node_id].id,
            sim.nodes[self.node_id].id,
            self.run_at,
            self.run_at + t
        )
        sim.events.put(nextEvent)

        # Create next transaction events for neighbours
        for peer_id in sim.nodes[self.node_id].peers:
            t = sim.latency(sim.nodes[self.node_id], sim.nodes[peer_id], 1)

            nextEvent = TransactionReceive(
                newTrans,
                peer_id,
                sim.nodes[self.node_id].id,
                self.run_at,
                self.run_at + t
            )
            sim.events.put(nextEvent)


class TransactionReceive(Event):

    def __init__(self, transaction, node_id, creator_id, created_at, run_at):
        super(TransactionReceive, self).__init__(
            node_id, creator_id, created_at, run_at
        )

        self.transaction = transaction

    def run(self, sim):

        # Check if this node has already seen this transaction before
        # If not, then add it to it's list
        # And generate TransactionReceive events for all its neighbours

        flag = False
        for x in sim.nodes[self.node_id].transactions:
            if x.id == self.transaction.id:
                flag = True
        if not flag:
            sim.nodes[self.node_id].transactions.append(self.transaction)
            for peer_id in sim.nodes[self.node_id].peers:
                t = sim.latency(sim.nodes[self.node_id], sim.nodes[peer_id], 1)
                nextEvent = TransactionReceive(
                    self.transaction, peer_id, sim.nodes[self.node_id].id, self.run_at, self.run_at + t)
                sim.events.put(nextEvent)


class BlockGenerate(Event):

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(BlockGenerate, self).__init__(
            node_id, creator_id, created_at, run_at
        )

    def run(self, sim):
        flag = False
        for x in sim.nodes[self.node_id].receivedStamps:
            if x > self.run_at:
                flag = True

        if not flag:
            leng = -1
            blk = None
            for x in sim.nodes[self.node_id].blocks:
                if x.len > leng:
                    leng = x.len
                    blk = x
                    # break
            newblk = Block(sim.block_id, self.run_at,
                           sim.nodes[self.node_id].id, blk.id, leng + 1)
            sim.block_id += 1
            for x in sim.nodes[self.node_id].transactions:
                prevblk = blk
                while (prevblk.id != 0):
                    if x in prevblk.transactions:
                        if x in sim.nodes[self.node_id].transactions:
                            sim.nodes[self.node_id].transactions.remove(x)
                    prevblk = sim.nodes[self.node_id].get(
                        prevblk.prev_block_id)

            newblk.transactions.extend(sim.nodes[self.node_id].transactions)
            sim.nodes[self.node_id].blocks.append(newblk)
            sim.nodes[self.node_id].coins += 50

            for peer_id in sim.nodes[self.node_id].peers:
                if peer_id != newblk.creator_id:
                    t = sim.latency(
                        sim.nodes[self.node_id], sim.nodes[peer_id], 1)
                    nextEvent = BlockReceive(
                        newblk, peer_id, sim.nodes[self.node_id].id, self.run_at, self.run_at + t)
                    sim.events.put(nextEvent)


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

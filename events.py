
from block import Block, Transaction
import random

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

        #@ankit
        toid = -1;
        while(toid == self.node_id):
            toid = randint(0,sim.n)

        factor = random.uniform(0,1)
        transAmt = self.node_id.coins*factor
        #need to add trans_id variable to simulator object.initial value 0
        self.node_id.coins -= transAmt
        toid.coins += transAmt
        newTrans = Transaction(sim.trans_id,self.node_id,toid,transAmt)
        sim.trans_id += 1
        self.transactions.append(newTrans)

        #add parameter lmbd to simulator for poisson distribution.value 10
        lmbd = 10;
        t = math.log(1-random.uniform(0,1))/(-lmbd)
        nextEvent = TransactionGenerate(self.node_id,self.node_id,self.run_at,self.run_at+t)
        sim.events.append(nextEvent)

        for peer_id in self.node_id.peers:
            #lmbd = 10;
            t = sim.prop_delay[self.node_id][peer_id]
            nextEvent = TransactionReceive(newTrans,peer_id,self.node_id,self.run_at,self.run_at+t)
            sim.events.append(nextEvent)
        raise NotImplementedError

class TransactionReceive(Event):

    def __init__(self, transaction, **kwargs):
        super(self).__init__(**kwargs)

        self.transaction = transaction

    def run(sim):

        # Check if this node has already seen this transaction before
        # If not, then add it to it's list
        # And generate TransactionReceive events for all its neighbours

        #@ankit
        flag = False
        for x in self.node_id.transactions:
            if x.trans_id == self.transaction.trans_id:
                flag = True
        if not flag:
            self.node_id.transactions.append(self.transaction)
            for peer_id in self.node_id.peers:
                #lmbd = 10;
                t = sim.prop_delay[self.node_id][peer_id]
                nextEvent = TransactionReceive(self.transaction,peer_id,self.node_id,self.run_at,self.run_at+t)
                sim.events.append(nextEvent)

        raise NotImplementedError


class BlockGenerate(Event):

    def __init__(self, **kwargs):
        super(self).__init__(**kwargs)

    def run(sim):
        flag = False
        for x in self.node_id.receivedStamps:
            if x > self.run_at
                flag = True

        if not flag:
            leng = 0
            blk = None
            for x in self.node_id.blocks:
                if x.len > leng:
                    leng = x.len
                    blk = x
                    break

            newblk = Block(s.block_id,self.run_at,self.node_id,blk,leng+1)
            for x in self.node_id.transactions:
                if x in blk.transactions:
                    self.node_id.transactions.remove(x)
                else
                    newblk.transactions.append(x)

            self.node_id.blocks.append(newblk)
            for peer_id in self.node_id.peers:
                #lmbd = 10;
                if peer_id != block.creator_id:
                    t = sim.prop_delay[self.node_id][peer_id]
                    nextEvent = BlockReceive(newblk,peer_id,self.node_id,self.run_at,self.run_at+t)
                    sim.events.append(nextEvent)
        raise NotImplementedError


class BlockReceive(Event):

    def __init__(self, block, **kwargs):
        super(self).__init__(**kwargs)

        self.block = block

    def run(sim):
        #@ankit
        flag = False
        for x in self.node_id.blocks:
            if x.block_id == self.block.block_id:
                flag = True

        if not flag:
            blk = None
            for x in self.node_id.blocks:
                if x.block_id == self.block.block_id:
                    blk = x
                    break

            newblk = Block(block.block_id,block.created_at,block.creator_id,blk.block_id)
            newblk.len += 1
            self.node_id.blocks.append(newblk)
            self.node_id.receivedStamps.append(newblk.created_at)

            for peer_id in self.node_id.peers:
                #lmbd = 10;
                if peer_id != block.creator_id:
                    t = sim.prop_delay[self.node_id][peer_id]
                    nextEvent = BlockReceive(self.block,peer_id,self.node_id,self.run_at,self.run_at+t)
                    sim.events.append(nextEvent)

            #Do we need a schedule time value to be passed as well.
            lmbd = 10;
            t = math.log(1-random.uniform(0,1))/(-lmbd)
            nextEvent = BlockGenerate(self.node_id,self.node_id,self.run_at,self.run_at+t)
            sim.events.append(nextEvent)
        raise NotImplementedError

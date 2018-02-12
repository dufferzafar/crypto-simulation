
from block import Block, Transaction
import random

class Event(object):

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(Block, self).__init__()

        # Node this event will happen on
        sim.nodes[self.node_id].id = node_id

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
        while(toid == sim.nodes[self.node_id].id):
            toid = randint(0,sim.n-1)

        factor = random.uniform(0,1)
        transAmt = sim.nodes[self.node_id].coins*factor
        #need to add trans_id variable to simulator object.initial value 0
        sim.nodes[self.node_id].coins -= transAmt
        toid.coins += transAmt
        newTrans = Transaction(sim.trans_id,sim.nodes[self.node_id].id,toid,transAmt)
        sim.trans_id += 1
        self.transactions.append(newTrans)

        #add parameter lmbd to simulator for poisson distribution.value 10
        lmbd = sim.nodes[self.node_id].lmbd;
        t = math.log(1-random.uniform(0,1))/(-lmbd)
        nextEvent = TransactionGenerate(sim.nodes[self.node_id].id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
        sim.events.append(nextEvent)

        for peer_id in sim.nodes[self.node_id].peers:
            #lmbd = 10;
            t = sim.latency(sim.nodes[self.node_id].id,peer_id,1);
            nextEvent = TransactionReceive(newTrans,peer_id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
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
        for x in sim.nodes[self.node_id].transactions:
            if x.trans_id == self.transaction.trans_id:
                flag = True
        if not flag:
            sim.nodes[self.node_id].transactions.append(self.transaction)
            for peer_id in sim.nodes[self.node_id].peers:
                #lmbd = 10;
                t = sim.latency(sim.nodes[self.node_id].id,peer_id,1);
                nextEvent = TransactionReceive(self.transaction,peer_id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
                sim.events.append(nextEvent)

        raise NotImplementedError


class BlockGenerate(Event):

    def __init__(self, **kwargs):
        super(self).__init__(**kwargs)

    def run(sim):
        flag = False
        for x in sim.nodes[self.node_id].receivedStamps:
            if x > self.run_at
                flag = True

        if not flag:
            leng = 0
            blk = None
            for x in sim.nodes[self.node_id].blocks:
                if x.len > leng:
                    leng = x.len
                    blk = x
                    break

            newblk = Block(sim.block_id,self.run_at,sim.nodes[self.node_id].id,blk,leng+1)
            sim.block_id += 1
            for x in sim.nodes[self.node_id].transactions:
                prevblk = blk;
                while (prevblk.block_id != 0):
                    if x in prevblk.transactions:
                        sim.nodes[self.node_id].transactions.remove(x)
                    prevblk = prevblk.prev_block_id

            newblk.transactions.extend(sim.nodes[self.node_id].transactions)
            sim.nodes[self.node_id].blocks.append(newblk)
            sim.nodes[self.node_id].coins += 50
            for peer_id in sim.nodes[self.node_id].peers:
                #lmbd = 10;
                if peer_id != block.creator_id:
                    t = sim.latency(sim.nodes[self.node_id].id,peer_id,1);
                    nextEvent = BlockReceive(newblk,peer_id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
                    sim.events.append(nextEvent)
        raise NotImplementedError


class BlockReceive(Event):

    def __init__(self, block, **kwargs):
        super(self).__init__(**kwargs)

        self.block = block

    def run(sim):
        #@ankit
        flag = False
        for x in sim.nodes[self.node_id].blocks:
            if x.block_id == self.block.block_id:
                flag = True

        if not flag:
            blk = None
            for x in sim.nodes[self.node_id].blocks:
                if x.block_id == self.block.block_id:
                    blk = x
                    break

            newblk = Block(block.block_id,block.created_at,block.creator_id,blk.block_id)
            newblk.len += 1
            sim.nodes[self.node_id].blocks.append(newblk)
            sim.nodes[self.node_id].receivedStamps.append(newblk.created_at)

            for peer_id in sim.nodes[self.node_id].peers:
                #lmbd = 10;
                if peer_id != block.creator_id:
                    t = sim.latency(sim.nodes[self.node_id].id,peer_id,1);
                    nextEvent = BlockReceive(self.block,peer_id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
                    sim.events.append(nextEvent)

            #Do we need a schedule time value to be passed as well.
            lmbd = sim.nodes[self.node_id].lmbd;
            t = math.log(1-random.uniform(0,1))/(-lmbd)
            nextEvent = BlockGenerate(sim.nodes[self.node_id].id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
            sim.events.append(nextEvent)
        raise NotImplementedError

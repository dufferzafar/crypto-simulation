
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

    #def __init__(self, **kwargs):
    #    super(TransactionGenerate,self).__init__(**kwargs)

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(TransactionGenerate,self).__init__(node_id, creator_id, created_at, run_at)

    def run(self,sim):

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
        sim.nodes[toid].coins += transAmt
        newTrans = Transaction(sim.trans_id,sim.nodes[self.node_id].id,toid,transAmt)
        sim.trans_id += 1
        sim.nodes[self.node_id].transactions.append(newTrans)

        #add parameter lmbd to simulator for poisson distribution.value 10
        lmbd = sim.lmbd;
        t = math.log(1-random.uniform(0,1))/(-lmbd)
        #print("%d\n",t)
        nextEvent = TransactionGenerate(sim.nodes[self.node_id].id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
        sim.events.put(nextEvent)

        for peer_id in sim.nodes[self.node_id].peers:
            #lmbd = 10;
            t = sim.latency(sim.nodes[self.node_id],sim.nodes[peer_id],1);
            nextEvent = TransactionReceive(newTrans,peer_id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
            sim.events.put(nextEvent)
        #raise NotImplementedError

class TransactionReceive(Event):

    #def __init__(self, transaction, **kwargs):
    #    super(TransactionReceive,self).__init__(**kwargs)

    def __init__(self, transaction, node_id, creator_id, created_at, run_at):
        super(TransactionReceive,self).__init__(node_id, creator_id, created_at, run_at)

        self.transaction = transaction

    def run(self,sim):

        # Check if this node has already seen this transaction before
        # If not, then add it to it's list
        # And generate TransactionReceive events for all its neighbours

        #@ankit
        flag = False
        for x in sim.nodes[self.node_id].transactions:
            if x.id == self.transaction.id:
                flag = True
        if not flag:
            sim.nodes[self.node_id].transactions.append(self.transaction)
            for peer_id in sim.nodes[self.node_id].peers:
                #lmbd = 10;
                t = sim.latency(sim.nodes[self.node_id],sim.nodes[peer_id],1);
                nextEvent = TransactionReceive(self.transaction,peer_id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
                sim.events.put(nextEvent)

        #raise NotImplementedError


class BlockGenerate(Event):

    #def __init__(self, **kwargs):
    #    super(BlockGenerate,self).__init__(**kwargs)

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(BlockGenerate, self).__init__(node_id, creator_id, created_at, run_at)

    def run(self,sim):
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
                    #break
            newblk = Block(sim.block_id,self.run_at,sim.nodes[self.node_id].id,blk.id,leng+1)
            sim.block_id += 1
            for x in sim.nodes[self.node_id].transactions:
                prevblk = blk;
                #print(prevblk)
                while (prevblk.id != 0):
                    if x in prevblk.transactions:
                        if x in sim.nodes[self.node_id].transactions:
                            sim.nodes[self.node_id].transactions.remove(x)
                    prevblk = sim.nodes[self.node_id].get(prevblk.prev_block_id)

            newblk.transactions.extend(sim.nodes[self.node_id].transactions)
            sim.nodes[self.node_id].blocks.append(newblk)
            sim.nodes[self.node_id].coins += 50
            for peer_id in sim.nodes[self.node_id].peers:
                #lmbd = 10;
                if peer_id != newblk.creator_id:
                    t = sim.latency(sim.nodes[self.node_id],sim.nodes[peer_id],1);
                    nextEvent = BlockReceive(newblk,peer_id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
                    sim.events.put(nextEvent)
        #raise NotImplementedError


class BlockReceive(Event):

    #def __init__(self, block, **kwargs):
    #    super(BlockReceive,self).__init__(**kwargs)
    #    self.block = block

    def __init__(self, block, node_id, creator_id, created_at, run_at):
        super(BlockReceive,self).__init__(node_id, creator_id, created_at, run_at)
        self.block = block

    def run(self,sim):
        #@ankit
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

            print(blk)
            print(self.block)
            #To break the loop if previous block does not exist in the current block chain. why????
            if blk is None:
                return
            newblk = Block(self.block.id,self.block.created_at,self.block.creator_id,blk.id,self.block.len)
            newblk.len += 1
            sim.nodes[self.node_id].blocks.append(newblk)
            sim.nodes[self.node_id].receivedStamps.append(newblk.created_at)

            for peer_id in sim.nodes[self.node_id].peers:
                #lmbd = 10;
                if peer_id != self.block.creator_id:
                    t = sim.latency(sim.nodes[self.node_id],sim.nodes[peer_id],1);
                    nextEvent = BlockReceive(self.block,peer_id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
                    sim.events.put(nextEvent)

            #Do we need a schedule time value to be passed as well.
            lmbd = sim.lmbd;
            t = math.log(1-random.uniform(0,1))/(-lmbd)
            nextEvent = BlockGenerate(sim.nodes[self.node_id].id,sim.nodes[self.node_id].id,self.run_at,self.run_at+t)
            sim.events.put(nextEvent)
        #raise NotImplementedError

"""
Used for debugging graph dumping and pruning of blockchains.
"""

from node import Node
from block import Block
from simulation import Simulator

if __name__ == '__main__':

    # Dummy node
    n = Node(1, 1, True)

    # Create a dummy simulator
    s = Simulator(0, 0, 0, 0)
    s.nodes = [n]

    # Manually created blockchain
    n.blocks.update({
        0: Block(0, 0.0, 0, -1, 0),
        1: Block(1, 0.0, 0, 0, 1),
        2: Block(2, 0.0, 0, 1, 2),
        3: Block(3, 5.0, 0, 2, 3),

        # Fork
        4: Block(4, 0.0, 0, 1, 2),
        5: Block(5, 0.0, 0, 4, 3),
    })

    # Dump graphs
    s.remove_graphs()
    s.dump_node_chains()
    s.prune_node_chains()
    s.dump_node_chains(pruned=True)
    s.convert_graphs()


# crypto-sim

A Discrete-event Simulator for a P2P Cryptocurrency Network.

Assignment 1 of COL 867 - High Speed Networks course at IIT Delhi taught by Prof. Vinay Ribeiro.


## Running the code

* We've used Python 3 on Ubuntu for testing.

* Chart outputs are stored in the `output/` directory

In the source directory, run:  `python3 run.py [n] [z] [tm] [bm]`

For eg: `python3 run.py 10 0.3 3 10`

By default, simulations run for a maximum of 1000 events. 

To change that pass `--until` parameter and to suppress printing of event log use `-q`:

For eg: `python3 run.py 10 0.3 3 10 -q --until 5000`

---

All these steps can also be performed at once, just by running `make`. See Makefile for more information.


## Grading

It turned out that our design was fundamentally flawed. We had to consider this as a distributed system problem and not have a centralized simulation controller.

Marks were deducted for this mistake. We ended up scoring 19.5/25.

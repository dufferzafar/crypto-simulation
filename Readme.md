
# crypto-sim

A Discrete-event Simulator for a P2P Cryptocurrency Network.

Assignment 1 of COL 867 - High Speed Networks course at IIT Delhi taught by Prof. Vinay Ribeiro.


## Running the code

* We've used Python 3 on Ubuntu for testing.

* Just run: `$ python3 run.py [n] [z] [mean] [max_events]`

as an example: `$ python3 run.py 10 0.3 100`

* Chart outputs are stored in the `output/` directory

* To convert the charts into PNG images, run:

`$ python3 graphs.py`

---

All these steps can also be performed at once, just by running `make`. See Makefile for more information.

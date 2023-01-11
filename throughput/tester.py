import multiprocessing
import argparse
import sys, os, time
import pdb
import datetime



from stimulation import *
from computation import *
from visualization import *



spin_spif_map = {"1": "172.16.223.2", 
                 "37": "172.16.223.106", 
                 "43": "172.16.223.98",
                 "13": "172.16.223.10",
                 "121": "172.16.223.122",
                 "129": "172.16.223.130"}

def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-b', '--board', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="1")
    parser.add_argument('-n', '--bin', type=float, help="Time bin in [s] (for event counts)", default=1.0)
    parser.add_argument('-i', '--ip', type= str, help="SPIF's IP address", default="172.16.223.2")
    parser.add_argument('-p', '--port', type=int, help="SPIF's port", default=3333)
    parser.add_argument('-r', '--remote-receiver', action="store_true", help="Remote Receiver")
    parser.add_argument('-s', '--simulate-spif', action="store_true", help="Simulate SPIF")
    parser.add_argument('-l', '--length', type=int, help="Unit size in px", default=40)
    parser.add_argument('-u', '--units', type=int, help="# of units per column/row", default=40)
    parser.add_argument('-w', '--weight', type=int, help="Kernel Weights", default=7)


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    current_datetime = datetime.datetime.now()
    if not args.simulate_spif:
        mode = "spif"
    else:
        mode = "enet"

    
    manager = multiprocessing.Manager()
    end_of_sim = manager.Value('i', 0)

    input_q = multiprocessing.Queue() # events

    stim = Stimulator(args, input_q, end_of_sim)

    with stim:
        time.sleep(stim.duration)
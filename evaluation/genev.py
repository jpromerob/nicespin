import multiprocessing
import argparse
import sys, os, time
import pdb



from stimulation import *
from computation import *
from visualization import *


def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-t','--runtime', type=int, help="Run Time, in seconds", default=60*20)
    parser.add_argument('-i', '--ip', type= str, help="SPIF's IP address", default="172.16.223.2")
    parser.add_argument('-p', '--port', type=int, help="SPIF's port", default=3333)
    parser.add_argument('-w', '--width', type=int, help="Image size (in px)", default=320)
    parser.add_argument('-g', '--height', type=int, help="Image size (in px)", default=320)
    parser.add_argument('-r', '--radius', type=int, help="Stimulus size (in px)", default=20)
    parser.add_argument('-s', '--simulate-spif', action="store_true", help="Simulate SPIF")


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    manager = multiprocessing.Manager()
    end_of_sim = manager.Value('i', 0)
    input_q = multiprocessing.Queue() # events
    output_q = multiprocessing.Queue() # events


    stim = Stimulator(args, input_q, end_of_sim)
    disp = Display(args, input_q, output_q, end_of_sim)

    with stim:
        with disp:

            time.sleep(args.runtime)
            end_of_sim.value = 1 # Let other processes know that simulation stopped
        

import multiprocessing 
import argparse
import sys, os, time
import pdb

# from new_stimulation import *
from fullstim import *


def parse_args():

    
    parser = argparse.ArgumentParser(description='Generator of Artificial Data')

    parser.add_argument('-t','--runtime', type=int, help="Run Time, in seconds", default=300)
    parser.add_argument('-i', '--ip', type= str, help="SPIF's IP address", default="172.16.223.98")
    parser.add_argument('-p', '--port', type=int, help="SPIF's port", default=3333)
    parser.add_argument('-w', '--width', type=int, help="Image size (in px)", default=64)
    parser.add_argument('-g', '--height', type=int, help="Image size (in px)", default=48)
    parser.add_argument('-r', '--radius', type=int, help="Stimulus radius (in px)", default=8)
    parser.add_argument('-z', '--t_sleep', type=float, help="Sleep time in ms ", default=100.0)
    parser.add_argument('-s', '--spif', action="store_true", help="Use SPIF")
    

    return parser.parse_args()
   

if __name__ == '__main__':

    args = parse_args()
        


    stim = Stimulator(args)


    with stim:
            
        time.sleep(args.runtime)
    


import subprocess
import threading
import time
import socket
import struct
from queue import Queue
import os
import csv
import argparse
import pdb
import numpy as np
from datetime import datetime



def parse_args():

    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation')

    parser.add_argument('-n', '--nb-threads', type= int, help="# of threads", default=1)   

    return parser.parse_args()
   

if __name__ == '__main__':


    args = parse_args()

    sleeper_array =  np.logspace(4,2, dtype='int')
    # sleeper_array = [800]

    # pdb.set_trace()

    width = 256
    ev_per_packet = 256
    nb_threads = args.nb_threads
    spif_ip = '172.16.223.10'
    filename = 'coords_xy.csv'

    for sleeper in sleeper_array:
        os.system(f'./threaded_csv_sender.exe {filename} {spif_ip} 3333 {width} {2000000} 1 1 1')
        time.sleep(1)
        os.system(f'./threaded_csv_sender.exe {filename} {spif_ip} 3333 {width} {int(sleeper)} 1 {ev_per_packet} {nb_threads}')
        time.sleep(5)
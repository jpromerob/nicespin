import multiprocessing
import socket
import pdb
import math
import sys
import datetime
import time
import numpy as np
import random
from struct import pack
import os
import ctypes
from time import sleep
import pyNN.spiNNaker as p


class Stimulator:
    def __init__(self, args, input_q, end_of_sim):

        # SNN parameters
        self.width = args.width
        self.height = args.height  
        self.ip = args.ip
        self.port = args.port
        self.duration = 60*30

        # Other Stuff
        self.t_sleeper_array = np.concatenate((np.logspace(4,1, num=200, base=10), np.array([8,4,2,1])))

        # Infrastructure parameters
        self.input_q = input_q 
        # self.input_q.put((ev_per_s, expected_count), False)
        self.p_stream = multiprocessing.Process(target=self.launch_input_handler, args=())

    def start_handler(self, label, connection):
        self.running.value = True

    def end_handler(self, label, connection):
        self.running.value = False

    def __enter__(self):
        self.p_stream.start()    

    def __exit__(self, e, b, t):
        self.end_of_sim.value = 1
        self.p_stream.join()



    def launch_input_handler(self):
        for t in self.t_sleeper_array:
            
            self.input_q.put(int(t), False)   
            command = f"~/fast_sender/sender {self.width} {self.height} {int(t)} {self.ip}:{self.port}"
            # print(command)
            os.system(command)

        
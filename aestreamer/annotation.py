import multiprocessing 
import socket
import pdb
import math
import sys
import os
import datetime
import time
import numpy as np
import random
import collections
import csv

NB_PTS = 100
LINE = "________________________________________"

class Writer:
    
    def __init__(self, args, input_q, output_q, end_of_sim, filename):

        self.input_q = input_q
        self.bin = args.bin
        self.output_q = output_q
        self.end_of_sim = end_of_sim
        self.filename = filename

        self.p_stats = multiprocessing.Process(target=self.get_stats, args=())
    
    def __enter__(self):
        self.p_stats.start()

    def __exit__(self, e, b, t):
        self.p_stats.join()

    def get_stats(self):
        
        ev_out_count = 0
        sleeper = 1000000

        write_line = False


        with open(self.filename, mode='w') as sim_file:  
            csv_writer = csv.writer(sim_file, delimiter=',')

            while True:
                
                # Check if the spinnaker simulation has ended
                if self.end_of_sim.value == 1:
                    time.sleep(1)
                    print("No more stats to be saved")
                    break

                # Get input vals counts ... 
                while not self.input_q.empty():
                    print(f"{sleeper}: {ev_out_count}ev/s")
                    sleeper = self.input_q.get(False)
                    ev_out_count = 0

                # Get output counts ...     
                while not self.output_q.empty():
                    ev_out_count += self.output_q.get(False)

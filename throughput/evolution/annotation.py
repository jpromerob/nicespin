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
        
        ev_in_count = 0
        ev_out_count = 0
        ev_expected = 0
        old_expected = 0

        write_line = False


        with open(self.filename, mode='w') as sim_file:  
            csv_writer = csv.writer(sim_file, delimiter=',')

            while True:
                
                # Check if the spinnaker simulation has ended
                if self.end_of_sim.value == 1:
                    time.sleep(1)
                    print("No more stats to be saved")
                    break


                while not self.input_q.empty():
                    in_data = self.input_q.get(False)
                    ev_in_count = in_data[0]
                    ev_expected = in_data[1]
                    write_line = True
                    
                while not self.output_q.empty():
                    ev_out_count = self.output_q.get(False)

                
                if write_line:
                    if old_expected <= ev_expected:
                        print(f"Exp:\t{ev_expected}\tIn:\t{ev_in_count}\tOut:\t{ev_out_count}")
                        csv_writer.writerow([ev_expected, ev_in_count, ev_out_count])
                        old_expected = ev_expected
                    else:
                        print("...")
                    write_line = False
                    ev_out_count = 0

                time.sleep(self.bin/4)
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

class Display:
    
    def __init__(self, args, input_q, output_q, end_of_sim, filename):

        self.width = args.width
        self.height = args.height
        self.input_q = input_q
        self.output_q = output_q
        self.end_of_sim = end_of_sim
        self.filename = filename

        self.p_stats = multiprocessing.Process(target=self.show_time, args=())
    
    def __enter__(self):
        self.p_stats.start()

    def __exit__(self, e, b, t):
        self.p_stats.join()

    def show_time(self):
        

        write_line = False
        t_in = t_out = -1
        x_in = y_in = -1
        x_out = y_out = -1


        with open(self.filename, mode='w') as sim_file:  
            csv_writer = csv.writer(sim_file, delimiter=',')

            while True:
                
                # Check if the spinnaker simulation has ended
                if self.end_of_sim.value == 1:
                    time.sleep(1)
                    print("No more stats to be saved")
                    break


                while not self.input_q.empty():
                    x_in, y_in, t_in = self.input_q.get()
                    # t_in = time.perf_counter()
                    # print(f"IN: Got ({x_in},{y_in}) ...")

                    
                while not self.output_q.empty():
                    id_out, t_out = self.output_q.get()
                    # t_out = time.perf_counter()
                       
                    x_out = int(id_out) % self.width
                    y_out = int(int(id_out) / self.width)
                    # print(f"OUT : Got ({x_out}, {y_out}) ...")
                    if x_out == x_in and y_out == y_in:
                        write_line = True
                        

                
                if write_line:
                    csv_writer.writerow([t_out-t_in, x_in, y_in, x_out, y_out])
                    write_line = False
                    t_in = t_out = -1
                    x_in = y_in = -1
                    x_out = y_out = -1
                
                

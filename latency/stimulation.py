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
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


class Stimulator:
    def __init__(self, args, input_q, end_of_sim):

        # SNN parameters
        self.width = args.width
        self.height = args.height       

        # Infrastructure parameters
        self.input_q = input_q
        self.end_of_sim = end_of_sim
        self.running = multiprocessing.Value(ctypes.c_bool)
        self.port = multiprocessing.Value(ctypes.c_uint32)
        self.running.value = False
        self.port.value = 0
        self.p_stream = multiprocessing.Process(target=self.launch_input_handler, args=())

        # SPIF/ENET parameters
        self.use_spif = not args.simulate_spif
        if self.use_spif:
            self.p_shift = 15
            self.y_shift = 0
            self.x_shift = 16
            self.no_timestamp = 0x80000000
            self.sock_data = b""
            self.ip_addr = args.ip
            self.spif_port = args.port
        else:
            self.spikes = []

        # Stuff that needs to be done    
        self.p_stream.start()        
        if not self.use_spif:
            while self.port.value == 0:
                time.sleep(0.1)

    def start_handler(self, label, connection):
        self.running.value = True

    def end_handler(self, label, connection):
        self.running.value = False

    def __enter__(self):
        time.sleep(0.1)

    def __exit__(self, e, b, t):
        self.end_of_sim.value = 1
        self.p_stream.join()


    def event_generator(self):  
        vert_motion  = False
        sq_len = min(self.width, self.height)

        while True: 
            x = random.randint(0,self.width-1)
            y = random.randint(0,self.height-1)
            yield ((x,y))  
                        

    def launch_input_handler(self):


        ev_gen = self.event_generator() 

        IN_POP_LABEL = "input"
        polarity = 1
        
        time.sleep(30) # Waiting for SpiNNaker to be ready

        if self.use_spif:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Using SPIF ({self.ip_addr}) on port {self.spif_port}")
        else:
            connection = p.external_devices.SpynnakerLiveSpikesConnection(send_labels=[IN_POP_LABEL], local_port=None)
            self.port.value = connection.local_port
            connection.add_start_resume_callback(IN_POP_LABEL, self.start_handler)
            connection.add_pause_stop_callback(IN_POP_LABEL, self.end_handler)
            print(f"Using ENET on port {self.port.value}")


        while self.end_of_sim.value == 0:
            
            

            if not self.use_spif and not self.running.value:
                continue
 
            e = next(ev_gen)
            
            x = e[0]
            y = e[1]

            if self.use_spif:
                packed = (self.no_timestamp + (polarity << self.p_shift) + (y << self.y_shift) + (x << self.x_shift))
                self.sock_data += pack("<I", packed)
            else:
                self.spikes.append((y * self.width) + x)

                
                

                
            if self.use_spif:                
                sock.sendto(self.sock_data, (self.ip_addr, self.spif_port))
                self.sock_data = b""
            elif self.spikes:                
                connection.send_spikes(IN_POP_LABEL, self.spikes)
                self.spikes = []

            # Send a packet of events every second  
            
            t_current = time.time()  
            # print(f"Sent ({x},{y}) at t={t_current}")
            self.input_q.put((x,y,t_current))
            time.sleep(0.1)

        print("No more events to be created")
        if self.use_spif:
            sock.close()
        else:
            connection.close()

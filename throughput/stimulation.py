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

        # Other Stuff
        self.bin = args.bin    
        self.t_sleeper_array = np.logspace(1.9,-0.9, num=200, base=10) #ms
        self.spin_waiter = 30
        self.time_per_point = 2*self.bin
        self.duration = self.time_per_point*len(self.t_sleeper_array) + self.spin_waiter

        # Infrastructure parameters
        self.input_q = input_q
        self.end_of_sim = end_of_sim
        self.running = multiprocessing.Value(ctypes.c_bool)
        self.port = multiprocessing.Value(ctypes.c_uint32)
        self.running.value = False
        self.port.value = 0
        self.p_stream = multiprocessing.Process(target=self.launch_input_handler, args=())

        # SPIF/ENET parameters
        self.mode = args.mode
            
        if self.mode[0] == 's':
            self.p_shift = 15
            self.y_shift = 0
            self.x_shift = 16
            self.no_timestamp = 0x80000000
            self.sock_data = b""
            self.ip_addr = args.ip
            self.spif_port = args.port
            
        if self.mode[0] == 'e':
            self.spikes = []

        # Stuff that needs to be done    
        self.p_stream.start()    
        
        if self.mode[0] == 'e':
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
        
        while True:
            for t_sleeper in self.t_sleeper_array:
                t_start = time.time()
                while True:
                    cx = 0
                    cy = 0
                    for y in range(self.height):
                        for x in range(self.width):
                            if x < self.width and y < self.height:
                                yield (x,y), t_sleeper
                    t_current =time.time()
                    if t_current >= t_start + self.time_per_point:
                        break
                        

    def launch_input_handler(self):

        # Create event generator
        ev_gen = self.event_generator() 
        IN_POP_LABEL = "input"        
        time.sleep(self.spin_waiter) # Waiting for SpiNNaker to be ready

        # Setting Communication Channels (sockets, ports, etc)
        if self.mode[0] == 's':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Using SPIF ({self.ip_addr}) on port {self.spif_port}")
        
        if self.mode[0] == 'e':
            connection = p.external_devices.SpynnakerLiveSpikesConnection(send_labels=[IN_POP_LABEL], local_port=None)
            self.port.value = connection.local_port
            connection.add_start_resume_callback(IN_POP_LABEL, self.start_handler)
            connection.add_pause_stop_callback(IN_POP_LABEL, self.end_handler)
            print(f"Using ENET on port {self.port.value}")


        # Looping until SpiNNaker ends simulation
        t_start = time.time()
        ev_count = 0
        while self.end_of_sim.value == 0:

            if self.mode[0] == 'e' and not self.running.value:
                continue

            # Pack as many events as indicated (pack_sz)
            pack_sz = 16*16
            for i in range(pack_sz):   

                e, t_sleeper = next(ev_gen)                
                x = e[0]
                y = e[1]
                ev_count +=1

                if self.mode[0] == 's':
                    polarity = 1
                    packed = (self.no_timestamp + (polarity << self.p_shift) + (y << self.y_shift) + (x << self.x_shift))
                    self.sock_data += pack("<I", packed)

                if self.mode[0] == 'e':
                    self.spikes.append((y * self.width) + x)

                t_current = time.time()  
                if t_current >= t_start + self.bin:
                    t_start = t_current
                    ev_per_s = int(ev_count/self.bin)
                    expected_count = int((1000/t_sleeper) * pack_sz)
                    self.input_q.put((ev_per_s, expected_count), False)
                    ev_count = 0
            
            # Send Packets of events
            if self.mode[0] == 's':
                sock.sendto(self.sock_data, (self.ip_addr, self.spif_port))
                self.sock_data = b""
            elif self.spikes:
                connection.send_spikes(IN_POP_LABEL, self.spikes)
                self.spikes = []

            # Sleep a bit
            time.sleep(t_sleeper/1000)

        # Close Communication Channels
        print("No more events to be created")
        if self.mode[0] == 's':
            sock.close()
        if self.mode[0] == 'e':
            connection.close()

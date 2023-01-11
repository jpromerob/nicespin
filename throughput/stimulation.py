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
        self.width = args.length
        self.height = args.length    
        self.units = args.units  
        self.streams = args.units
        self.in_pop_label = "input"

        # Other Stuff
        self.spin_waiter = 60
        self.bin = args.bin    
        self.max_ev_count = 1000*100
        self.t_wait_list = np.round(np.concatenate((np.logspace(4,1,40),np.linspace(9,1,9))),1)
        self.nb_steps = len(self.t_wait_list)
        self.points = 10
        self.time_per_point = self.points*self.bin # seconds
        self.duration = self.time_per_point*self.nb_steps + self.spin_waiter
        
        print("These are the waiting times ... ")
        print(self.t_wait_list)
        # pdb.set_trace()

        # Infrastructure parameters
        self.input_q = input_q
        self.end_of_sim = end_of_sim
        self.running = multiprocessing.Value(ctypes.c_bool)
        self.port = multiprocessing.Value(ctypes.c_uint32)
        self.running.value = False
        self.port.value = 0

        self.p_stream = []
        for s_id in range(self.streams):
            self.p_stream.append(multiprocessing.Process(target=self.launch_input_handler, args=(s_id,)))

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
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Using SPIF ({self.ip_addr}) on port {self.spif_port}")
        else:
            self.spikes = []
            self.connection = p.external_devices.SpynnakerLiveSpikesConnection(send_labels=[self.in_pop_label], local_port=None)
            self.port.value = self.connection.local_port
            self.connection.add_start_resume_callback(self.in_pop_label, self.start_handler)
            self.connection.add_pause_stop_callback(self.in_pop_label, self.end_handler)
            print(f"Using ENET on port {self.port.value}")

        # Stuff that needs to be done 
        
        for s_id in range(self.streams):   
            self.p_stream[s_id].start()        
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
        for s_id in range(self.streams):   
            self.p_stream[s_id].join()


    def event_generator(self):  

        xy_array = np.linspace(0, self.width*self.height-1, self.width*self.height)
        random.shuffle(xy_array)

        for t_wait in self.t_wait_list:
            t_start = time.time()
            while True:
                for idx in range(len(xy_array)):
                    x = int(xy_array[idx]/self.width)
                    y = int(xy_array[idx]%self.width)
                    yield ((x,y)), t_wait                                
                t_current =time.time()
                if t_current >= t_start + self.time_per_point:
                    break
                        

    def launch_input_handler(self, sender_id):

        ev_gen = self.event_generator()         

        polarity = 1
        ev_count = 0       
        
        t_start = time.time()
        pack_sz = 16*16

        divider = (self.width*self.height)/pack_sz
        
        time.sleep(self.spin_waiter) # Waiting for SpiNNaker to be ready
        print(f"Sender #{sender_id} is now active")

        while self.end_of_sim.value == 0:

            if not self.use_spif and not self.running.value:
                continue

            for i in range(pack_sz):   
                try:
                    e, t_wait = next(ev_gen)
                except:
                    print("No more events to be yielded ...")
                    time.sleep(1)
                    break
                
                x = e[0]
                y = e[1]

                if self.use_spif:
                    packed = (self.no_timestamp + (polarity << self.p_shift) + (y << self.y_shift) + (x << self.x_shift))
                    self.sock_data += pack("<I", packed)
                else:
                    self.spikes.append((y * self.width) + x)

                    
                t_current = time.time()  
                if t_current >= t_start + self.bin:
                    t_start = t_current
                    ev_per_s = int(ev_count/self.bin)
                    expected_count = 0
                    
                    # print(f"[T]: {expected_count} ev/s vs T: {ev_per_s} ev/s with t={round(t_wait,0)}[ms]")
                    self.input_q.put((ev_per_s, expected_count, sender_id), False)
                    ev_count = 0
                ev_count +=1

                
            if self.use_spif:     
                self.sock.sendto(self.sock_data, (self.ip_addr, self.spif_port))
                self.sock_data = b""
            elif self.spikes:      
                self.connection.send_spikes(self.in_pop_label, self.spikes)
                self.spikes = []
            
            time.sleep((t_wait/divider)/1000)

        print("No more events to be created")
        if self.use_spif:
            self.sock.close()
        else:
            self.connection.close()

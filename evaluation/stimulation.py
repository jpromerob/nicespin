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

        # Other Stuff
        self.bin = args.bin    
        self.min_freq = 25
        self.max_freq = 375
        self.step = 5
        self.points = 30
        self.time_per_point = self.points*self.bin # seconds
        self.nb_steps = int(1+(self.max_freq-self.min_freq)/self.step)
        self.duration = self.time_per_point*self.nb_steps

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
            
            freq_list = np.linspace(self.min_freq,self.max_freq,self.nb_steps)
            
            for freq in freq_list:
                t_start = time.time()
                while True:
                    cx = 0
                    cy = 0
                    for y in range(sq_len):
                        for x in range(sq_len):
                            # print(f"event at ({x},{y})")
                            if x < self.width and y < self.height:
                                yield ((x,y)), (freq)
                                
                    t_current =time.time()
                    if t_current >= t_start + self.time_per_point:
                        break
                        

    def launch_input_handler(self):


        ev_gen = self.event_generator() 

        IN_POP_LABEL = "input"

        polarity = 1
        ev_count = 0     
        var_sleeper_ms = 50.1    

        
        blink_count = 0
        t_start = time.time()
        t_last_blink = time.time()
        going_up = False
        step = 1
        min_step = 0.0001
        max_k_evs_ms = 1000*min(self.width, self.height)**2
        pack_sz = 16*16
        old_freq = 10
        we_send_stuff = False
        
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

            for i in range(pack_sz):   
                e, freq = next(ev_gen)
                if old_freq != freq:
                    var_sleeper_ms = 50.1
                    step = 10
                    old_freq = freq
                    going_up = False
                    time.sleep(self.bin*2) #To get rid of 'old' events in the neck
                
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
                    expected_count = int(freq*min(self.width,self.height)**2)
                    
                    # Error in Ev Count needs to be within the 5% margin to be reported
                    error = 100*abs(ev_per_s-expected_count)/expected_count
                    if error < 5:
                        # print(f"Input -->\tT:\t{ev_per_s}\t[T]:\t{expected_count}\te:\t{int(error*10)/10}%\tf:\t{freq}")
                        self.input_q.put((ev_per_s, expected_count), False)
                        we_send_stuff = True
                    else:
                        we_send_stuff = False
                        # print(f"...-->\tT:\t{ev_per_s}\t[T]:\t{expected_count}\te:\t{int(error*10)/10}%\tf:\t{freq}\tvs:\t{var_sleeper_ms}")
                        
                        
                    
                    if ev_per_s > int(max_k_evs_ms*freq/1000):
                        if not going_up and step >= min_step:
                            step = step / 5
                            going_up = True
                        var_sleeper_ms += step
                    else:
                        if going_up and step >= min_step:
                            step = step / 5
                            going_up = False
                        var_sleeper_ms -= step
                    
                    ev_count = 0
                ev_count +=1
                blink_count += 1

                
            if self.use_spif:                
                if we_send_stuff:
                    sock.sendto(self.sock_data, (self.ip_addr, self.spif_port))
                self.sock_data = b""
            elif self.spikes:                
                if we_send_stuff:
                    connection.send_spikes(IN_POP_LABEL, self.spikes)
                self.spikes = []

            if var_sleeper_ms > 0:
                time.sleep(var_sleeper_ms/1000)

        print("No more events to be created")
        if self.use_spif:
            sock.close()
        else:
            connection.close()

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
from struct import pack
import threading

# SpiNNaker imports
import pyNN.spiNNaker as p
from pyNN.space import Grid2D

class Computer:

    def __init__(self, args, output_q, stim):

        # SpiNNaker Parameters
        self.run_time = int(stim.duration)*1000 # in [ms]
        self.npc_x = 8
        self.npc_y = 4
        self.board = int(args.board)
        if self.board == 1:
            self.nb_boards = 24
        else:
            self.nb_boards = 1
        self.cfg_file = f"spynnaker_{self.board}.cfg"

        # Infrastructure Parameters
        self.output_q = output_q

        # SPIF/ENET Parameters
        self.mode = args.mode
        
        if self.mode[0] == 's':
            self.chip = (0,0)
            self.spif_port_in = args.port
            self.pipe = args.port-3333
            self.sub_height = 8
            self.sub_width = 16  
        if self.mode[1] == 's':
            self.chip = (0,0)
            self.spif_ip = args.ip
            self.spif_port_out = 3332      
            self.p_shift = 15
            self.y_shift = 0
            self.x_shift = 16
            self.no_timestamp = 0x80000000
            self.sock_data = b""
            
        if self.mode[0] == 'e':
            self.database_port = stim.port.value
        if self.mode[1] == 'e':
            self.port_spin2cpu = int(random.randint(12000,15000))

        # SNN Parameters
        self.width = args.width
        self.height = args.height

        # Stats 
        self.t_start = 0
        self.ev_count = 0 
        self.first_ev_sent = False
        self.bin_t = args.bin/2 # N second-bins to count events
        self.printer = threading.Thread(target=self.print_ev_count, args=())
        self.printer.start()


    def __enter__(self):


        ###############################################################################################################
        # SpiNNaker Configuration
        ###############################################################################################################
        p.setup(timestep=1.0, n_boards_required=self.nb_boards, cfg_file=self.cfg_file)
        p.set_number_of_neurons_per_core(p.IF_curr_exp, (self.npc_x, self.npc_y))


        ###############################################################################################################
        # Set Inputs
        ###############################################################################################################

        print("\n\n\n\n\n")

        IN_POP_LABEL = "input"
        if self.mode[0] == 's':
            print(f"Using SPIF ({self.spif_ip}) SPIFRetinaDevice on port {self.spif_port_in}")
            input_pop = p.Population(self.width * self.height, p.external_devices.SPIFRetinaDevice(
                                    pipe=self.pipe, width=self.width, height=self.height, 
                                    sub_width=self.sub_width, sub_height=self.sub_height, 
                                    chip_coords=self.chip), label=IN_POP_LABEL)
        else:
            print(f"Using ENET's SpikeInjector on port {self.database_port}")
            input_pop = p.Population(self.width * self.height, p.external_devices.SpikeInjector(
                                    database_notify_port_num=self.database_port), label=IN_POP_LABEL,
                                    structure=Grid2D(self.width / self.height))

        ###############################################################################################################
        # Set Outputs
        ###############################################################################################################
        
        OUT_POP_LABEL = "output"

        if self.mode[1] == 's':
            conn = p.external_devices.SPIFLiveSpikesConnection([IN_POP_LABEL], self.spif_ip, self.spif_port_out)
            conn.add_receive_callback(IN_POP_LABEL, self.recv_spif)
            print(f"Using SPIF ({self.spif_ip}) SPIFLiveSpikesConnection on port {self.spif_port_out}")

            output_pop = p.Population(None, p.external_devices.SPIFOutputDevice(
                database_notify_port_num=conn.local_port, chip_coords=self.chip), label=OUT_POP_LABEL)
            p.external_devices.activate_live_output_to(input_pop, output_pop)
            

        else:
            conn = p.external_devices.SpynnakerLiveSpikesConnection(receive_labels=[IN_POP_LABEL], local_port=self.port_spin2cpu)
            _ = p.external_devices.activate_live_output_for(input_pop, database_notify_port_num=conn.local_port)
            conn.add_receive_callback(IN_POP_LABEL, self.recv_enet)
            print(f"Using ENET's SpynnakerLiveSpikesConnection on port {conn.local_port}")
        
        print("\n\n\n\n\n")


    def __exit__(self, e, b, t):
        p.end()

    def print_ev_count(self):
        time.sleep(20)
        t_sleep = 1
        while True:
            if self.ev_count > 0:
                print(f"Ev count = {self.ev_count/t_sleep}\n", end='')
                self.ev_count = 0
            time.sleep(t_sleep)

    def recv_enet(self, label, t_spike, neuron_ids):
        self.ev_count += len(neuron_ids)

    def recv_spif(self, label, spikes):
        self.ev_count += len(spikes)

   
    def run_sim(self):
        p.run(self.run_time)
        time.sleep(0.1)

    def wrap_up(self):
        time.sleep(1)
        # Get recordings from populations (in case they exist)
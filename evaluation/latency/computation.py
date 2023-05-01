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

# SpiNNaker imports
import pyNN.spiNNaker as p
from pyNN.space import Grid2D

class Computer:

    def __init__(self, args, output_q, stim):
        # SpiNNaker Parameters
        self.run_time = args.runtime*1000 # in [ms]
        self.timestep = args.timestep/1000 # from [us] to [ms]
        print(f"Time Step: {self.timestep} [ms]")
        self.npc_x = 8
        self.npc_y = 4
        self.nb_boards = 1        
        try:
            self.board = args.board
            self.cfg_file = f"spynnaker_{self.board}.cfg"
        except:
            print("Wrong SpiNN-5 Board")

        # Infrastructure Parameters
        self.output_q = output_q

        # SPIF/ENET Parameters
        self.use_spif = not args.simulate_spif
        if self.use_spif:
            self.spif_ip = args.ip
            self.spif_port_out = 3332
            self.pipe = args.port-3333
            self.chip = (0,0)
            self.sub_height = 8
            self.sub_width = 16        
            self.p_shift = 15
            self.y_shift = 0
            self.x_shift = 16
            self.no_timestamp = 0x80000000
            self.sock_data = b""
        else:
            self.port_spin2cpu = int(random.randint(12000,15000))

        # SNN Parameters
        self.width = args.width
        self.height = args.height
        self.weight = args.weight
        self.database_port = stim.port.value


    def __enter__(self):


        ###############################################################################################################
        # SpiNNaker Configuration
        ###############################################################################################################

        p.setup(timestep=self.timestep, n_boards_required=self.nb_boards, cfg_file=self.cfg_file)
        p.set_number_of_neurons_per_core(p.IF_curr_exp, (self.npc_x, self.npc_y))


        ###############################################################################################################
        # Set Inputs
        ###############################################################################################################

        IN_POP_LABEL = "input"

        if self.use_spif:
            print("Using SPIFRetinaDevice")
            input_pop = p.Population(self.width * self.height, p.external_devices.SPIFRetinaDevice(
                                    pipe=self.pipe, width=self.width, height=self.height, 
                                    sub_width=self.sub_width, sub_height=self.sub_height, 
                                    chip_coords=self.chip), label=IN_POP_LABEL)
        else:
            print("Using SpikeInjector")
            input_pop = p.Population(self.width * self.height, p.external_devices.SpikeInjector(
                                    database_notify_port_num=self.database_port), label=IN_POP_LABEL,
                                    structure=Grid2D(self.width / self.height))
    

        ###############################################################################################################
        # Set Outputs
        ###############################################################################################################
        
        OUT_POP_LABEL = "output"

        if self.use_spif:
            print("Using SPIFOutputDevice")
            conn = p.external_devices.SPIFLiveSpikesConnection([IN_POP_LABEL], self.spif_ip, self.spif_port_out)
            conn.add_receive_callback(IN_POP_LABEL, self.recv_spif)
            output_pop = p.Population(None, p.external_devices.SPIFOutputDevice(
                database_notify_port_num=conn.local_port, chip_coords=self.chip), label=OUT_POP_LABEL)
            p.external_devices.activate_live_output_to(input_pop, output_pop)            

        else:
            print("Using SpynnakerLiveSpikesConnection")
            conn = p.external_devices.SpynnakerLiveSpikesConnection(receive_labels=[IN_POP_LABEL], local_port=self.port_spin2cpu)
            _ = p.external_devices.activate_live_output_for(input_pop, database_notify_port_num=conn.local_port)
            conn.add_receive_callback(IN_POP_LABEL, self.recv_enet)
        
        print("\n\n\n\n\n")


    def __exit__(self, e, b, t):
        p.end()


    def recv_enet(self, label, t_spike, neuron_ids):
        # t_current = time.perf_counter()
        t_current = time.monotonic()
        for n_id in neuron_ids:     
            self.output_q.put((n_id, t_current))



    def recv_spif(self, label, spikes):
        # t_current = time.perf_counter()
        t_current = time.monotonic()
        np_spikes = np.array(spikes)    
        for i in range(np_spikes.shape[0]):      
            self.output_q.put((np_spikes[i], t_current))      
        

    def run_sim(self):
        p.run(self.run_time)
        time.sleep(0.1)

    def wrap_up(self):
        time.sleep(1)
        # Get recordings from populations (in case they exist)
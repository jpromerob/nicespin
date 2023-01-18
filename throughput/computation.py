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





def create_lut(w, h, sw, sh):    

    delay = 1 # 1 [ms]
    nb_col = math.ceil(w/sw)
    nb_row = math.ceil(h/sh)

    lut = np.zeros((w*h,2), dtype='uint16')

    lut_ix = 0
    for h_block in range(nb_row):
        for v_block in range(nb_col):
            for row in range(sh):
                for col in range(sw):
                    x = v_block*sw+col
                    y = h_block*sh+row
                    if x<w and y<h:
                        # print(f"{lut_ix} -> ({x},{y})")
                        lut[lut_ix] = [x,y]
                        lut_ix += 1
        
    return lut


class Computer:

    def __init__(self, args, output_q, stim):
        # SpiNNaker Parameters
        self.run_time = int(stim.duration)*1000 # in [ms]
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
        self.mode = args.mode

        # Other Stuff
        self.lut = []
        
        if self.mode[0] == 's':
            self.chip = (0,0)
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
        self.weight = args.weight/10
        self.direct = args.direct

        # Cell Parameters
        self.tau_refrac = args.tau_ref/1000
        self.celltype = p.IF_curr_exp
        self.cell_params = {'tau_m': 20.0,
                            'tau_syn_E': 5.0,
                            'tau_syn_I': 5.0,
                            'v_rest': -65.0,
                            'v_reset': -65.0,
                            'v_thresh': -50.0,
                            'tau_refrac': self.tau_refrac, # 0.1 originally
                            'cm': 1,
                            'i_offset': 0.0
                            }

        # Remote receiver's parameters
        self.remote_receiver = args.remote_receiver
        if self.remote_receiver:
            self.pc_ip = "172.16.222.199"
            self.pc_port = 3000
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Stats 
        self.t_start = 0
        self.ev_count = 0 
        self.first_ev_sent = False
        self.bin_t = args.bin/2 # N second-bins to count events


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
        # SNN
        ###############################################################################################################

        if self.direct:
            
            # Output Mapping using LUT
            self.lut = create_lut(self.width, self.height, self.npc_x, self.npc_y)

            PRE_OUT_POP_LABEL = IN_POP_LABEL 
            pre_out_pop = input_pop

        else:

            # Convolution
            kernel = np.ones((1, 1))*(self.weight)

            convolution = p.ConvolutionConnector(kernel_weights=kernel)
            out_width, out_height = convolution.get_post_shape((self.width, self.height))

            # Target population
            MID_POP_LABEL = "middle"
            middle_pop = p.Population(
                out_width * out_height, p.IF_curr_exp(),
                structure=p.Grid2D(out_width / out_height), label=MID_POP_LABEL)

            # Projection from Input to Middle 
            p.Projection(input_pop, middle_pop, convolution, p.Convolution())

            # Output Mapping using LUT
            self.lut = create_lut(out_width, out_height, self.npc_x, self.npc_y)
            
            PRE_OUT_POP_LABEL = MID_POP_LABEL 
            pre_out_pop = middle_pop


        ###############################################################################################################
        # Set Outputs
        ###############################################################################################################
        
        OUT_POP_LABEL = "output"

        if self.mode[1] == 's':
            print("Using SPIFOutputDevice")
            conn = p.external_devices.SPIFLiveSpikesConnection([PRE_OUT_POP_LABEL], self.spif_ip, self.spif_port_out)
            conn.add_receive_callback(PRE_OUT_POP_LABEL, self.recv_spif)

            output_pop = p.Population(None, p.external_devices.SPIFOutputDevice(
                database_notify_port_num=conn.local_port, chip_coords=self.chip), label=OUT_POP_LABEL)
            p.external_devices.activate_live_output_to(pre_out_pop, output_pop)
            

        else:
            print("Using SpynnakerLiveSpikesConnection")
            conn = p.external_devices.SpynnakerLiveSpikesConnection(receive_labels=[PRE_OUT_POP_LABEL], local_port=self.port_spin2cpu)
            _ = p.external_devices.activate_live_output_for(pre_out_pop, database_notify_port_num=conn.local_port)
            conn.add_receive_callback(PRE_OUT_POP_LABEL, self.recv_enet)
        
        print("\n\n\n\n\n")


    def __exit__(self, e, b, t):
        p.end()


    def recv_enet(self, label, t_spike, neuron_ids):

        for n_id in neuron_ids:     
        # np_neuron_ids = np.array(neuron_ids)
        # for i in range(np_neuron_ids.shape[0]):       
            self.update_stats()
            
            if self.remote_receiver:
                time.sleep(0.000001)

        
        self.publish_stats()


    def recv_spif(self, label, spikes):

        np_spikes = np.array(spikes)
        for i in range(np_spikes.shape[0]):
            self.update_stats()

            if self.remote_receiver:
                x = self.lut[np_spikes[i]][0]
                y = self.lut[np_spikes[i]][1]
                polarity = 1
                packed = (self.no_timestamp + (polarity << self.p_shift) + (y << self.y_shift) + (x << self.x_shift))
                self.sock_data += pack("<I", packed)
                if i+1 == np_spikes.shape[0]:
                    self.sock.sendto(self.sock_data, (self.pc_ip, self.pc_port))
                    self.sock_data = b""
        

        self.publish_stats()
    

    def update_stats(self):
        if not self.first_ev_sent:
            self.first_ev_sent = True
            self.t_start = time.time()
        self.ev_count += 1


    def publish_stats(self):        
        if self.first_ev_sent:
            t_current = time.time()
            if t_current >= self.t_start + self.bin_t:
                ev_per_s = int(self.ev_count/self.bin_t)
                self.output_q.put(ev_per_s, False)                
                self.t_start = t_current
                self.ev_count = 0

        

    def run_sim(self):
        p.run(self.run_time)
        time.sleep(0.1)

    def wrap_up(self):
        time.sleep(1)
        # Get recordings from populations (in case they exist)
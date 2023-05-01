import numpy as np
import math
import pyNN.spiNNaker as p
import pdb
import socket
from struct import pack
import matplotlib.pyplot as plt
import argparse
import time
import os

def forward_events(np_spikes, width, pc_ip, pc_port, sock):
    
        data = b""

        P_SHIFT = 15
        Y_SHIFT = 0
        X_SHIFT = 16
        NO_TIMESTAMP = 0x80000000
        for i in range(np_spikes.shape[0]):
            polarity = 1
            x = int(np_spikes[i] % width)
            y = int(np_spikes[i] / width)
            packed = (NO_TIMESTAMP + (polarity << P_SHIFT) + (y << Y_SHIFT) + (x << X_SHIFT))
            data += pack("<I", packed)
        sock.sendto(data, (pc_ip, pc_port))

class Computer:

    def __init__(self, args):

        # SpiNNaker simulation parameters
        self.npc_x = args.npc_x
        self.npc_y = args.npc_y
        self.runtime = 1000*args.runtime
        self.board = int(args.board)
        self.cfg_file = f"spynnaker_{self.board}.cfg"



        self.celltype = p.IF_curr_exp
        self.cell_params = {'tau_m': 2.0, # 20 originally
                            'tau_syn_E': 1.0, # 5.0 originally
                            'tau_syn_I': 1.0, # 5.0 originally
                            'v_rest': -65.0,
                            'v_reset': -65.0,
                            'v_thresh': -60.0, # -50 originally
                            'tau_refrac': 0.0, # 0.1 originally
                            'cm': 1,
                            'i_offset': 0.0
                            }
        self.weight = args.weight



        # SPIF parameters
        self.width = args.width
        self.height = args.height
        self.chip = (0,0)
        self.spif_in_port = args.in_port
        self.pipe = self.spif_in_port - 3333
        self.spif_ip = args.spif_ip
        self.spif_out_port = args.out_port
        print(f"SPIF @ {args.spif_ip}")

        # Visualizer
        self.pc_ip = args.pc_ip
        self.pc_port = args.pc_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direct = args.direct
        self.print_data()


    def print_data(self):

        message = "Simulation Summary:\n"
        message += f"   - runtime: {self.runtime} seconds\n"
        message += f"   - with {self.npc_x}*{self.npc_y} neurons per core\n"
        message += f"   - direct mode: {self.direct}\n"
        message += f"   - SPIF @{self.spif_ip}\n"
        message += f"      - input port: {self.spif_in_port}\n"
        message += f"      - output port: {self.spif_out_port}\n"
        message += f"      - width: {self.width}\n"
        message += f"      - height: {self.height}\n"
        message += f"      - weight: {self.weight}\n"
        message += f"      - # cores used: {int((self.width*self.height)/(self.npc_x*self.npc_y))}\n"
        if self.pc_ip != "":
            message += f"   - Client @{self.pc_ip}, port {self.pc_port}\n"
        message += "\n Is this correct? "
        print(message)
        time.sleep(5)

    def __enter__(self):

        p.setup(timestep=1.0, n_boards_required=1, cfg_file=self.cfg_file)
        p.set_number_of_neurons_per_core(p.IF_curr_exp, (self.npc_x, self.npc_y))



        ###############################################################################################################
        # Set SPIF Input
        ###############################################################################################################
        IN_POP_LABEL = "input"
        print("Using SPIFRetinaDevice")
        input_pop = p.Population(None, p.external_devices.SPIFInputDevice(
                                pipe=self.pipe, n_neurons=self.width*self.height,
                                n_neurons_per_partition=self.npc_x*self.npc_y,
                                chip_coords=self.chip), label=IN_POP_LABEL)

        ###############################################################################################################
        # Set SPIF Output
        ###############################################################################################################
        if self.direct:

            OUT_POP_LABEL = "output"

            print("Using SPIFOutputDevice")
            conn = p.external_devices.SPIFLiveSpikesConnection([IN_POP_LABEL],self.spif_ip, self.spif_out_port)
            # conn.add_receive_callback(IN_POP_LABEL, self.recv_spif)
            output_pop = p.Population(None, p.external_devices.SPIFOutputDevice(
                database_notify_port_num=conn.local_port, chip_coords=self.chip), label=OUT_POP_LABEL)
            p.external_devices.activate_live_output_to(input_pop, output_pop)

        else:

            MID_POP_LABEL = "middle"
            middle_pop = p.Population(self.width*self.height, self.celltype(**self.cell_params), label=MID_POP_LABEL)
            p.Projection(input_pop, middle_pop, p.OneToOneConnector(), p.StaticSynapse(weight=self.weight))

            OUT_POP_LABEL = "output"

            print("Using SPIFOutputDevice")
            conn = p.external_devices.SPIFLiveSpikesConnection([MID_POP_LABEL],self.spif_ip, self.spif_out_port, events_per_packet=256, time_per_packet=10)
            # conn.add_receive_callback(MID_POP_LABEL, self.recv_spif)
            output_pop = p.Population(None, p.external_devices.SPIFOutputDevice(
                database_notify_port_num=conn.local_port, chip_coords=self.chip), label=OUT_POP_LABEL)
            p.external_devices.activate_live_output_to(middle_pop, output_pop)


    def recv_spif(self, label, spikes):

        np_spikes = np.array(spikes)  
        # forward_events(np_spikes, self.width, self.pc_ip, self.pc_port, self.sock)    


    def run_sim(self):
        p.run(self.runtime)


    def __exit__(self, e, b, t):
        p.end()

spin_spif_map = {"1": "172.16.223.2", 
                 "37": "172.16.223.106", 
                 "43": "172.16.223.98",
                 "13": "172.16.223.10",
                 "121": "172.16.223.122",
                 "129": "172.16.223.130"}

def parse_args():

    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation')

    parser.add_argument('-d', '--direct', action='store_true', help="indirect")  # on/off flag

    # SpiNNaker Simulation Parameters
    parser.add_argument('-nx', '--npc-x', type=int, help="# Neurons Per Core (x)", default=8)
    parser.add_argument('-ny', '--npc-y', type=int, help="# Neurons Per Core (y)", default=8)
    parser.add_argument('-r','--runtime', type=int, help="Run Time, in seconds", default=60*240)
    parser.add_argument('-b', '--board', type= str, help="SpiNN-5 Board IP x.x.x.<X>", default="1")

    parser.add_argument('-w','--weight', type=float, help="Weight (per synapse)", default=2.0)

    # SPIF parameters
    parser.add_argument('-pi', '--in-port', type=int, help="SPIF's port", default=3333)
    parser.add_argument('-po', '--out-port', type=int, help="SPIF's port", default=3332)    
    parser.add_argument('-x', '--width', type=int, help="Image width (in px)", default=256)
    parser.add_argument('-y', '--height', type=int, help="Image height (in px)", default=128)

    # 'Visualizer' Parameters (i.e a PC where to display SPIF's Output)
    parser.add_argument('-ip', '--pc-ip', type= str, help="PC IP address", default="10.37.222.2")
    parser.add_argument('-p', '--pc-port', type=int, help="PC port", default=3331)    

    return parser.parse_args()
   

if __name__ == '__main__':

    args = parse_args()
    # pdb.set_trace()
    args.spif_ip = spin_spif_map[args.board]


    try:
        # pdb.set_trace()
        os.system("clear")
        rig_command = f"rig-power 172.16.223.{int(args.board)-1}"
        print(f"Currently waiting for '{rig_command}' to end")
        os.system(rig_command)
    except:
        print("Wrong SpiNN-5 to SPIF mapping")
        quit()

    spin = Computer(args)


    with spin:
        spin.run_sim()
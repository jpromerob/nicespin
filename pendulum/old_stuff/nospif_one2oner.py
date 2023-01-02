import numpy as np
import math
import pyNN.spiNNaker as p
import pdb
import time
import socket

import random
from pyNN.space import Grid2D
from struct import pack
import matplotlib.pyplot as plt


##########################################################################
# SPIF CONFIG
##########################################################################
USING_SPIF = False
if USING_SPIF:
    SPIF_IP = "172.16.223.2"
    SPIF_PORT = 3332
    CHIP = (0, 0)
    SUB_HEIGHT = 16
    SUB_WIDTH = SUB_HEIGHT*2

else:
    PORT_SPIN2CPU = int(random.randint(12000,15000))


##########################################################################
# MORE CONFIG
##########################################################################

NPC_X = 8
NPC_Y = 4

WIDTH = 320
HEIGHT = WIDTH

NB_BOARDS = 24



MY_PC_IP = "172.16.222.199"
MY_PC_PORT = 3331
POP_LABEL = "target"
RUN_TIME = 1000*60*20




##########################################################################
# CONVOLUTION PART
##########################################################################
kernel = np.ones((1, 1))*10



convolution = p.ConvolutionConnector(kernel_weights=kernel)
out_width, out_height = convolution.get_post_shape((WIDTH, HEIGHT))


##########################################################################
# OUTPUTTING EVENTS
##########################################################################


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



P_SHIFT = 15
Y_SHIFT = 0
X_SHIFT = 16
NO_TIMESTAMP = 0x80000000


global sock 
global lut
global ev_count
global first_ev_sent
global t_start

ev_count = 0
first_ev_sent = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lut = create_lut(out_width, out_height, NPC_X, NPC_Y)



def recv_nid(label, spikes):
    global sock
    global lut
    global t_start
    global ev_count
    global first_ev_sent

    data = b""
    np_spikes = np.array(spikes)
    # print(np_spikes.shape)
    for i in range(np_spikes.shape[0]):
        if not first_ev_sent:
            first_ev_sent = True
            t_start = time.time()
        ev_count += 1
        x = lut[np_spikes[i]][0]
        y = lut[np_spikes[i]][1]
        polarity = 1
        # print(f"{np_spikes[i]} --> ({lut[np_spikes[i]][0]}, {lut[np_spikes[i]][1]})")
        packed = (NO_TIMESTAMP + (polarity << P_SHIFT) + (y << Y_SHIFT) + (x << X_SHIFT))
        data += pack("<I", packed)
    sock.sendto(data, (MY_PC_IP, MY_PC_PORT))
    

    if first_ev_sent:
        t_current = time.time()
        if t_current >= t_start + 4:
            print(f"{ev_count/4} ev/s")
            t_start = t_current
            ev_count = 0




##########################################################################
# SPINNAKER SETUP
##########################################################################

p.setup(timestep=1.0, n_boards_required=NB_BOARDS)
p.set_number_of_neurons_per_core(p.IF_curr_exp, (NPC_X, NPC_Y))

##########################################################################
# SNN
##########################################################################

if USING_SPIF:
    retina = p.Population(
        WIDTH * HEIGHT, p.external_devices.SPIFRetinaDevice(
            pipe=0, width=WIDTH, height=HEIGHT,
            sub_width=SUB_WIDTH, sub_height=SUB_HEIGHT, chip_coords=CHIP),
        label="retina")
else:
    retina = p.Population(WIDTH*HEIGHT, p.external_devices.SpikeInjector(
        database_notify_port_num=0), label="retina",
        structure=Grid2D(WIDTH / HEIGHT))

target_pop = p.Population(
    out_width * out_height, p.IF_curr_exp(),
    structure=p.Grid2D(out_width / out_height), label=POP_LABEL)
# target_pop.record("spikes")

p.Projection(retina, target_pop, convolution, p.Convolution())

if USING_SPIF:
    conn = p.external_devices.SPIFLiveSpikesConnection([POP_LABEL], SPIF_IP, SPIF_PORT)
    conn.add_receive_callback(POP_LABEL, recv_nid)

    spif_output = p.Population(None, p.external_devices.SPIFOutputDevice(
        database_notify_port_num=conn.local_port, chip_coords=CHIP), label="output")
    p.external_devices.activate_live_output_to(target_pop, spif_output)
else:
    # Spike reception (from SpiNNaker to CPU)
    conn = p.external_devices.SpynnakerLiveSpikesConnection(receive_labels=[POP_LABEL], local_port=47908)
    _ = p.external_devices.activate_live_output_for(target_pop, database_notify_port_num=conn.local_port)
    conn.add_receive_callback(POP_LABEL, recv_nid)

p.run(RUN_TIME)

p.end()


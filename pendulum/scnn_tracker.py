import numpy as np
import math
import pyNN.spiNNaker as p
import pdb
import socket
from struct import pack
import matplotlib.pyplot as plt

def make_kernel_circle(r, k_sz,weight, kernel):
    # pdb.set_trace()
    var = int((k_sz+1)/2-1)
    a = np.arange(0, 2 * math.pi, 0.01)
    dx = np.round(r * np.sin(a)).astype("uint32")
    dy = np.round(r * np.cos(a)).astype("uint32")
    kernel[var + dx, var + dy] = weight


# scaler = 0.1
# SUB_WIDTH = 16
# SUB_HEIGHT = 8
# NPC_X = 8
# NPC_Y = 4
# WIDTH = 640
# HEIGHT = 640


# WIDTH = 640
# HEIGHT = int(WIDTH*3/4)

# This seems to work OK-ish
# scaler = 0.08
# SUB_WIDTH = 16
# SUB_HEIGHT = 8
# NPC_X = 16
# NPC_Y = 4
# WIDTH = 320
# HEIGHT = 320

# ... ?
# scaler = 0.08
# SUB_WIDTH = 16
# SUB_HEIGHT = 8
# NPC_X = 16
# NPC_Y = 4
# WIDTH = 640
# HEIGHT = 640

# # THIS WORKS!
scaler = 0.08
SUB_WIDTH = 16
SUB_HEIGHT = 8
NPC_X = 8
NPC_Y = 4
WIDTH = 640
HEIGHT = 640

# # This one 'loaded' for loooong and then it failed
# scaler = 0.08
# SUB_WIDTH = 16
# SUB_HEIGHT = 8
# NPC_X = 8
# NPC_Y = 4
# WIDTH = 720
# HEIGHT = 720

# This one 'loaded' for loooong and then it failed
# SUB_WIDTH = 16
# SUB_HEIGHT = 8
# NPC_X = 16
# NPC_Y = 8
# WIDTH = 1280
# HEIGHT = 720




SPIF_IP = "172.16.223.2"
SPIF_PORT = 3332
MY_PC_IP = "10.37.222.2"
MY_PC_PORT = 3331
POP_LABEL = "target"
RUN_TIME = 1000*60*240
CHIP = (0, 0)


# The one in the video (using original recordings)
k_sz = 39
pos_w = 0.8
neg_w = -1.0
print(k_sz)
kernel = np.zeros((k_sz, k_sz))
make_kernel_circle(0.46*k_sz, k_sz, pos_w*scaler, kernel)
make_kernel_circle(0.41*k_sz, k_sz, neg_w*scaler, kernel)
make_kernel_circle(0.36*k_sz, k_sz, pos_w*scaler, kernel)
make_kernel_circle(0.26*k_sz, k_sz, neg_w*scaler, kernel)

plt.imshow(kernel, interpolation='nearest')
plt.savefig("images/kernel.png")


convolution = p.ConvolutionConnector(kernel_weights=kernel)
out_width, out_height = convolution.get_post_shape((WIDTH, HEIGHT))

print(f"Output {out_width} x {out_height}")


P_SHIFT = 15
Y_SHIFT = 0
X_SHIFT = 16
NO_TIMESTAMP = 0x80000000


global sock 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def recv_nid(label, spikes):
    global sock
    data = b""
    np_spikes = np.array(spikes)
    for i in range(np_spikes.shape[0]):        
        x = int(np_spikes[i]) % out_width
        y = int(int(np_spikes[i]) / out_width)
        polarity = 1
        packed = (NO_TIMESTAMP + (polarity << P_SHIFT) + (y << Y_SHIFT) + (x << X_SHIFT))
        data += pack("<I", packed)
    sock.sendto(data, (MY_PC_IP, MY_PC_PORT))



conn = p.external_devices.SPIFLiveSpikesConnection(
    [POP_LABEL], SPIF_IP, SPIF_PORT)
conn.add_receive_callback(POP_LABEL, recv_nid)


p.setup(timestep=1.0, n_boards_required=24)
p.set_number_of_neurons_per_core(p.IF_curr_exp, (NPC_X, NPC_Y))

spif_retina = p.Population(
    WIDTH * HEIGHT, p.external_devices.SPIFRetinaDevice(
        pipe=0, width=WIDTH, height=HEIGHT,
        sub_width=SUB_WIDTH, sub_height=SUB_HEIGHT, chip_coords=CHIP),
    label="retina")

target_pop = p.Population(
    out_width * out_height, p.IF_curr_exp(),
    structure=p.Grid2D(out_width / out_height), label=POP_LABEL)

p.Projection(spif_retina, target_pop, convolution, p.Convolution())

spif_output = p.Population(None, p.external_devices.SPIFOutputDevice(
    database_notify_port_num=conn.local_port, chip_coords=CHIP), label="output")
p.external_devices.activate_live_output_to(target_pop, spif_output)


p.run(RUN_TIME)

p.end()


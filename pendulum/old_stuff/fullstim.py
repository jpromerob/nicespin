
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

import pyNN.spiNNaker as p

# An event frame has 32 bits <t[31]><x [30:16]><p [15]><y [14:0]>
P_SHIFT = 15
Y_SHIFT = 0
X_SHIFT = 16
NO_TIMESTAMP = 0x80000000





class Stimulator:
    def __init__(self, args):
        self.display = []
        self.ip_addr = args.ip
        self.port = args.port
        self.local_port = 0
        self.radius = args.radius
        self.w = args.width
        self.h = args.height
        self.t_sleep = args.t_sleep
        self.use_spif = args.spif
        self.flag = False
        self.display_size = (346, int(self.h*346/self.w))
        self.pix_mat_mp = multiprocessing.Array('I', int(np.prod((self.w, self.h))), lock=multiprocessing.Lock())
        self.pix_mat_np = np.frombuffer(self.pix_mat_mp.get_obj(), dtype='I').reshape((self.w, self.h))
        self.shared_pix_mat = (self.pix_mat_mp, self.pix_mat_np)
        if self.use_spif:
            print("Use SPIF")
            time.sleep(5)
            self.p_stream_1 = multiprocessing.Process(target=self.spif_input_handler, args=())
            self.p_stream_2 = multiprocessing.Process(target=self.spif_input_handler, args=())
            self.p_stream_3 = multiprocessing.Process(target=self.spif_input_handler, args=())
            self.p_stream_4 = multiprocessing.Process(target=self.spif_input_handler, args=())
        else:
            print("No Use SPIF")
            time.sleep(5)
            self.p_stream_0 = multiprocessing.Process(target=self.nospif_input_handler, args=())
            self.p_stream_0.start()
            while self.local_port == 0:
                time.sleep(0.1)
            print(f"LOCAL PORT is : {self.local_port}")
            time.sleep(10)
    
    def __enter__(self):
        if self.use_spif:
            self.p_stream_1.start()
            self.p_stream_2.start()
            self.p_stream_3.start()
            self.p_stream_4.start()
    
    def __exit__(self, e, b, t): 
        if self.use_spif:
            self.p_stream_1.join()
            self.p_stream_2.join()
            self.p_stream_3.join()
            self.p_stream_4.join()
        else:
            self.p_stream_0.join()
    
    def start_handler(self, label, connection):
        self.flag = True

    def end_handler(self, label, connection):
        self.flag = False

    def give_me_ev(self):  
        vert_motion  = False
        step = int(self.radius*0.8)
        while True: 
            if vert_motion:
                for cy in range(int(self.h/step)):
                    for cx in range(int(self.w/step)):
                        # print(f"center at ({cx*step},{cy*step}) ***********")
                        for y in range(self.radius):
                            for x in range(self.radius):
                                # print(f"event at ({cx*step+x},{cy*step+y})")
                                if cx*step+x < self.w and cy*step+y < self.h:
                                    yield ((cx*step+x,cy*step+y))
                        time.sleep(self.t_sleep/1000)
                vert_motion = True

            else:
                for cx in range(int(self.w/step)):
                    for cy in range(int(self.h/step)):
                        # print(f"center at ({cx*step},{cy*step}) ***********")
                        for x in range(self.radius):
                            for y in range(self.radius):
                                # print(f"event at ({cx*step+x},{cy*step+y})")
                                if cx*step+x < self.w and cy*step+y < self.h:
                                    yield ((cx*step+x,cy*step+y))
                        time.sleep(self.t_sleep/1000+0.001)
                vert_motion = True

    def spif_input_handler(self):

        polarity = 1
        ev_count = 0

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        ev_gen = self.give_me_ev() 
        t_start = time.time()
        while True:       

            pack_sz = 16*16
            data = b""
            for i in range(pack_sz):   
                e = next(ev_gen)
                ev_count +=1
                x = e[0]
                y = e[1]
                # print(f"center at ({x},{y}) #####################################")
                t_current = time.time()    
                if t_current >= t_start + 4:
                    t_start = t_current
                    print(f"{ev_count/4} ev/s")
                    ev_count = 0
            
                packed = (
                    NO_TIMESTAMP + (polarity << P_SHIFT) +
                    (y << Y_SHIFT) + (x << X_SHIFT))

                data += pack("<I", packed)
            sock.sendto(data, (self.ip_addr, self.port))
    

    def nospif_input_handler(self):

        
        ev_gen = self.give_me_ev()
        ev_count = 0
        t_start = time.time()

        connection = p.external_devices.SpynnakerLiveSpikesConnection(send_labels=["retina"], local_port=48706)
        self.local_port = connection.local_port
        print(f"\n\n\n{self.local_port}\n\n\n")
        connection.add_start_resume_callback("retina", self.start_handler)
        connection.add_pause_stop_callback("retina", self.end_handler)

        while True:
            spikes = []
            pack_sz = 16*16
            for i in range(pack_sz):   
                e = next(ev_gen)
                ev_count +=1
                t_current = time.time()   
                if t_current >= t_start + 4:
                    t_start = t_current
                    print(f"{ev_count/4} ev/s")
                    ev_count = 0
                spikes.append((e[1]*self.w )+e[0])
            connection.send_spikes("retina", spikes)
        
        connection.close()
                





        

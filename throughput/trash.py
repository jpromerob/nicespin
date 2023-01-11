
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



def event_generator(t_wait_list):  
    for t_wait in t_wait_list:
       yield t_wait

def find_expected(pack_sz, t_wait, divider):
    val = int(pack_sz*1000/(t_wait/divider))
    return pack_sz*int((val/pack_sz+1))
    
nb_pixels = 32*32
t_wait = 501 #[ms]
max_ev_count = 1000*100
step = 20
t_wait_list = np.round(np.concatenate((np.logspace(3.3,1,40),np.linspace(9,1,9),np.linspace(0.9,0.1,9))),1)

print(t_wait_list)
print(len(t_wait_list))

toto = event_generator(t_wait_list)


pack_sz = 16*16
full_sz = 256*256
print(find_expected(pack_sz, 1159, full_sz/pack_sz))
print(find_expected(pack_sz, 1012, full_sz/pack_sz))
pdb.set_trace()


import torch
import aestream
import time
import cv2
import pdb
import numpy as np
import math
import argparse
import csv
import os

# pdb.set_trace()


parser = argparse.ArgumentParser(description='Visualizer')
parser.add_argument('-p1', '--port1', type= int, help="Port for input", default=3331)
parser.add_argument('-p2', '--port2', type= int, help="Port for output", default=3332)
parser.add_argument('-s', '--scale', type= float, help="Image scale", default=1)
parser.add_argument('-x', '--in_width', type= int, help="X res = in_width", default=640)
parser.add_argument('-y', '--in_height', type= int, help="Y res = in_height", default=480)
parser.add_argument('-k', '--kernel', type= int, help="Kernel size", default=0)
parser.add_argument('-t', '--target', action="store_true", help="Show target")
parser.add_argument('-z', '--zoom', action="store_true", help="Zoom In (no offset)")

args = parser.parse_args()

e_port_1 = args.port1
in_width = args.in_width
in_height = args.in_height

e_port_2 = args.port2
offset = math.floor(args.kernel/2)
out_width = args.in_width-offset*2
out_height = args.in_height-offset*2


cv2.namedWindow('Durin On Board')

# Stream events from UDP port 3333 (default)
black = np.zeros((out_width, out_height,3))

in_frame = np.zeros((in_width,in_height,3))
out_frame = np.zeros((2*offset+out_width,2*offset+out_height,3))


high_x = 0
high_y = 0

radius = 4

# pdb.set_trace()

nx = args.scale
ny = args.scale
with aestream.UDPInput((in_width, in_height), device = 'cpu', port=e_port_1) as stream1:
    with aestream.UDPInput((out_width, out_height), device = 'cpu', port=e_port_2) as stream2:
            
        while True:

            in_frame[:,:,:] = np.zeros((in_width, in_height,3))
            out_frame[offset:offset+out_width,offset:offset+out_height,:] = black
            in_frame[:,:,1] = stream1.read().numpy() # Provides a (in_width, in_height) tensor
            out_frame[offset:offset+out_width,offset:offset+out_height,1] = stream2.read().numpy() # Provides a (out_width, out_height) tensor


            
            if args.target:

                # high_x = int(np.argmax(out_frame.sum(2).sum(1)))
                # high_y = int(np.argmax(out_frame.sum(2).sum(0)))
                line_x = out_frame[offset:offset+out_width,offset:offset+out_height,:].sum(2).sum(1)
                line_y = out_frame[offset:offset+out_width,offset:offset+out_height,:].sum(2).sum(0)
                idx_max_x = np.argwhere(line_x>=line_x.max())
                idx_max_y = np.argwhere(line_y>=line_y.max())

                if len(idx_max_x) > 0 and len(idx_max_y) > 0:
                    # pdb.set_trace()
                    high_x = int(np.average(idx_max_x))
                    high_y = int(np.average(idx_max_y))


                    # print(f"({high_x},{high_y})")


                    lim_left = high_x - radius
                    lim_right = high_x + radius
                    lim_up = high_y + radius
                    lim_bottom = high_y - radius
                    if(lim_left<0):
                        lim_left = 0
                    if(lim_bottom<0):
                        lim_bottom = 0
                    if(lim_right>=out_width):
                        lim_right = out_width-1
                    if(lim_up>=out_height):
                        lim_up = out_height-1

                    # Actual 'target' drawing
                    if out_frame[offset:offset+out_width,offset:offset+out_height,:].sum() > 1:
                        for x in range(lim_right-lim_left+1):
                            for y in range(lim_up-lim_bottom+1):
                                in_frame[offset+lim_left+x, offset+lim_bottom+y, :] = [0,0,255]

                
            image = cv2.resize(in_frame.transpose(1,0,2), (math.ceil(in_width*nx),math.ceil(in_height*ny)), interpolation = cv2.INTER_AREA)
            
            
            cv2.imshow('Durin On Board', image)
            cv2.waitKey(1)

    


        

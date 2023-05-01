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


'''
This script captures events on two ports: p1 and p2
Events captured on p1 are displayed as they come
Events captured on p2 are 'analyzed' so as to find center of activity
    ~ once found:
        - the center of activity is highlighted with a red square
        - the (x,y) coordinated of the center of activity are stored in a file

For this script to be useful there are some requirements:
    1. The Pendulum-tracking SCNN must be running on SpiNNaker
    2. A 'live' stream of events must be sent to:
        - the active SCNN
    3. SPIF must be configured so it forwards SCNN's output to this script's host (on p2)

'''

parser = argparse.ArgumentParser(description='Event Visualizer')

parser.add_argument('-p1', '--port1', type= int, help="Port for input", default=3331)
parser.add_argument('-p2', '--port2', type= int, help="Port for output", default=3332)
parser.add_argument('-p', '--period', type= int, help="Printing Period in ms", default=1000)
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


cv2.namedWindow('Pendulum Display')

# Stream events from UDP port 3333 (default)
black = np.zeros((out_width, out_height,3))

in_frame = np.zeros((in_width,in_height,3))
out_frame = np.zeros((2*offset+out_width,2*offset+out_height,3))


high_x = 0
high_y = 0
period = args.period/1000

radius = 4

nx = args.scale
ny = args.scale

with open('data/trajectory.csv', mode='w') as pendulum_file:  
    
    csv_writer = csv.writer(pendulum_file, delimiter=',')
    with aestream.UDPInput((in_width, in_height), device = 'cpu', port=e_port_1) as stream1:
        with aestream.UDPInput((out_width, out_height), device = 'cpu', port=e_port_2) as stream2:
            zero_time = time.time()    
            last_time = zero_time
            while True:

                in_frame[:,:,:] = np.zeros((in_width, in_height,3))
                out_frame[offset:offset+out_width,offset:offset+out_height,:] = black
                in_frame[:,:,1] = stream1.read().numpy() 
                out_frame[offset:offset+out_width,offset:offset+out_height,1] = stream2.read().numpy() 


                if args.target:

                    line_x = out_frame[offset:offset+out_width,offset:offset+out_height,:].sum(2).sum(1)
                    line_y = out_frame[offset:offset+out_width,offset:offset+out_height,:].sum(2).sum(0)
                    idx_max_x = np.argwhere(line_x>=line_x.max())
                    idx_max_y = np.argwhere(line_y>=line_y.max())

                    if len(idx_max_x) > 0 and len(idx_max_y) > 0:
                        # pdb.set_trace()
                        high_x = int(np.average(idx_max_x))
                        high_y = int(np.average(idx_max_y))


                        current_time = time.time()  # get the current time again
                        if (current_time > last_time + period and line_x.sum() > 0):  # calculate the elapsed time
                            csv_writer.writerow([high_x, high_y, current_time-zero_time])
                            last_time = current_time


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
                
                
                cv2.imshow('Pendulum Display', image)
                cv2.waitKey(1)

    


        

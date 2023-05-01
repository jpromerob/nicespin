import numpy as np
import csv
import argparse
import pdb

def parse_args():

    parser = argparse.ArgumentParser(description='Generation of Event Patterns')

    parser.add_argument('-x', '--width', type=int, help="Image width (in px)", default=256)
    parser.add_argument('-y', '--height', type=int, help="Image height (in px)", default=128)

    parser.add_argument('-nx', '--npc-x', type=int, help="# Neurons Per Core (x)", default=8)
    parser.add_argument('-ny', '--npc-y', type=int, help="# Neurons Per Core (y)", default=8) 

    parser.add_argument('-s', '--ev-per-packet', type=int, help="Events per packet", default=256) 


    return parser.parse_args()
   

if __name__ == '__main__':

    args = parse_args()
    
    nb_pixels = args.width*args.height    
    nb_npc = args.npc_x*args.npc_y    
    nb_cores = (nb_pixels)/(nb_npc)

    # Generate N random (x,y) coordinates
    coords = np.zeros((nb_pixels, 2), dtype='int')

    nb_cpr = int(args.width/nb_npc) # nb of cores per row
    nb_row = args.height

    stuff = np.zeros((nb_npc, nb_cpr, nb_row), dtype='int')

    n_id = 0
    for idx_3 in range(nb_row):
        for idx_2 in range(nb_cpr):
            for idx_1 in range(nb_npc):
                stuff[idx_1, idx_2, idx_3] = n_id
                n_id += 1



    # Save the coordinates to a CSV file
    with open('data/coords_xy.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        for idx_1 in range(nb_npc):
            for idx_3 in range(nb_row):
                for idx_2 in range(nb_cpr):
                    n_id = stuff[idx_1, idx_2, idx_3]
                    x = int(n_id % args.width)
                    y = int(n_id / args.width)
                    print(f"{n_id}: ({x}, {y})")
                    writer.writerow([x,y])
                    
    with open('data/coords_yx.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        for idx_1 in range(nb_npc):
            for idx_3 in range(nb_row):
                for idx_2 in range(nb_cpr):
                    n_id = stuff[idx_1, idx_2, idx_3]
                    x = int(n_id % args.width)
                    y = int(n_id / args.width)
                    print(f"{n_id}: ({x}, {y})")
                    writer.writerow([y,x])
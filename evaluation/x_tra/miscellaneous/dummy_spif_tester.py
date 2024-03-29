
from datetime import datetime

import argparse
import sys, os, time
import pdb
import numpy as np
import pdb


spin_spif_map = {"1": "172.16.223.2", 
                 "37": "172.16.223.106", 
                 "43": "172.16.223.98",
                 "13": "172.16.223.10",
                 "121": "172.16.223.122",
                 "129": "172.16.223.130"}




def parse_args():

    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation')

    # SpiNNaker Simulation Parameters
    parser.add_argument('-x', '--width', type=int, help="Image width (in px)", default=640)
    parser.add_argument('-y', '--height', type=int, help="Image height (in px)", default=480)
    parser.add_argument('-s', '--sleeper', type=int, help="time sleeper", default=2000000)
    parser.add_argument('-b', '--board', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="13")
    parser.add_argument('-p','--port', type=int, help="Run Time, in seconds", default=3333)
    parser.add_argument('-r','--p-request', type=int, help="Run Time, in seconds", default=4000)

    return parser.parse_args()


def create_sleeper_array(op_mode):


    sleeper_full_list = []
    pack_size_full_list = []
    if op_mode == "boxplots_1e6_steps":

        pack_size_list = [128, 128, 128, 128, 256, 256, 256, 256]
        sleeper_base_list = [196, 68, 26, 4, 38, 23, 11, 2]
        # sleeper_base_list = [444, 192, 107, 65, 38, 23, 11, 2]
        nb_runs = 10
        idx = 0
        for idx in range(len(sleeper_base_list)):
            for run in range(nb_runs):
                # print(sleeper)
                sleeper_full_list.append(sleeper_base_list[idx])
                pack_size_full_list.append(pack_size_list[idx])
        sleeper_array = np.array(sleeper_full_list)
        pack_size_array = np.array(pack_size_full_list)

    if op_mode == "sweep_range":
        pack_size_array = [256]
        sleeper_array = np.concatenate(([2000000],np.logspace(6.31,4,20), np.logspace(3.9,0,100)))

    return sleeper_array, pack_size_array


if __name__ == '__main__':


    os.system('rm my_data.csv')

    args = parse_args()

    
    op_mode = "boxplots_1e6_steps"


    date_string = datetime.now().strftime("%Y%m%d_%Hh%M")
    sleeper_array, pack_size_array = create_sleeper_array(op_mode)

    args.spif_ip = spin_spif_map[str(args.board)]


    # get the current time before the code
    start_time = time.time()



    
        
    filename = f"{op_mode}_{date_string}.csv"

    idx = 0
    for idx in range(len(sleeper_array)):
        sleeper = sleeper_array[idx]
        if op_mode == "boxplots_1e6_steps":
            pack_size = pack_size_array[idx]
        else:
            pack_size = pack_size_array[0]
        cmd = f"./send_and_request.exe {args.width} {args.height} {int(sleeper)} {args.spif_ip}:{args.port} {args.p_request} 1 {pack_size}"
        print(cmd)
        os.system(cmd) 
        time.sleep(0.2)
        idx += 1

    # calculate the elapsed time
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.5f} seconds")
    os.system(f"mv my_data.csv {filename}")
    time.sleep(5)

   
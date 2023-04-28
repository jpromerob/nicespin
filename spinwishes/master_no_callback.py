import subprocess
import threading
import time
from queue import Queue
import os
import csv
import argparse
import numpy as np
from datetime import datetime


def start_receiver(args, q_sender, q_receiver, q_data):
    
    while(True):
        value = q_receiver.get()  # Wait for the other function to put a value in the queue
        if value == "start_receiver":
            q_sender.put("start_sender")
            try:
                cmd = f"./c_code/spif_receiver.exe {args.spif_ip} {args.ev_per_pack} {args.exduration}"
                # print(f"Start Receiver: {cmd}")
                output = subprocess.check_output(cmd, shell=True)
                output_str = output.decode('utf-8') # convert bytes to string   
            except: 
                output_str = "0\n"
            q_data.put((1, output_str)) 
            # print(f"\n Packets captured :{output_str}")
        elif value == "stop_all":
            break


def start_sender(args, q_sender, q_receiver, q_data):

    q_receiver.put("start_receiver")
    
    # sleeper_base_list = [2e6, 37, 2e6, 38, 2e6, 39, 2e6, 37, 2e6, 38, 2e6, 39, 2e6, 37, 2e6, 38, 2e6, 39]
    sleeper_base_list = [444, 192, 107, 65, 37, 23, 11, 2, 1]
    # sleeper_base_list = np.logspace(1.6,0,20)
    # sleeper_base_list = np.linspace(100,1,100)
    # sleeper_base_list = np.concatenate(([2000000, 2000000],np.logspace(6.31,4,20), np.logspace(3.9,1.6,500), np.logspace(1.6,0,20)))
    # sleeper_base_list = [444, 192]

    
    start_time = time.time()

    idx = 0
    while(True):
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        print("\n")
        if idx == 0:
            print(f"Remaining time: unknown")
        else:
            print(f"Remaining time: {int(elapsed_time/idx*len(sleeper_base_list))}")
        print(f"Sleeper: {round(sleeper_base_list[idx],3)} [us] ({idx+1}/{len(sleeper_base_list)})")
        value = q_sender.get()  # Wait for the other function to put a value in the queue
        if value == "start_sender":
            time.sleep(1)
            cmd = f"./c_code/send_and_request.exe {args.width} {args.height} {int(sleeper_base_list[idx])} {args.spif_ip}:3333 4000 1 {args.ev_per_pack}"
            # print(f"Start Sender: {cmd}")
            output = subprocess.check_output(cmd, shell=True)
            ev_data = output.decode('utf-8')
            q_data.put((0,ev_data[0:-1]))
            time.sleep(args.exduration)
            cmd = f"./send_and_request.exe {args.width} {args.height} 1000000 {args.spif_ip}:3333 4000 1 1 "
            os.system(cmd) 
            time.sleep(1)
            
            idx+=1
            if idx >= len(sleeper_base_list):
                q_receiver.put("stop_all")
                q_data.put((2,0))
                time.sleep(2)
                break
            else:                
                q_receiver.put("start_receiver")


def print_data(args, q_data):

    tcp_dump_val = ""
    sender_val = ""

    summary = []

    now = datetime.now()
    date_time = now.strftime("%y%m%d_%Hh%M") 
    while True:
        value = q_data.get() 
        if value[0] == 0:
            sender_val = value[1]
        if value[0] == 1:
            tcp_dump_val = value[1]
        if value[0] == 2:
            break
        
        if tcp_dump_val != "" and sender_val != "":
            line = f"{sender_val},{tcp_dump_val[0:-1]}"
            val_array = line.split(',')

            with open(f"receiver_{args.ev_per_pack}_{date_time}.csv", 'a', newline='') as file:  
                writer = csv.writer(file, delimiter=',')
                writer.writerow(line.split(','))

            print(f"\tEv sent to SPIF: {val_array[0]}")
            print(f"\tEv handled by SPIF (in): {val_array[1]}")
            print(f"\tEv handled by SPIF (out): {val_array[4]}")
            print(f"\tEv captured by c++: {val_array[7]}")
            print(f"\tRatio c++ vs SPIF(out): {round(100*int(val_array[7])/int(val_array[4]),2)}%")
            tcp_dump_val = ""
            sender_val = ""

    time.sleep(2)
    # print("\n\n\n")
    


spin_spif_map = {"1": "172.16.223.2", 
                 "37": "172.16.223.106", 
                 "43": "172.16.223.98",
                 "13": "172.16.223.10",
                 "121": "172.16.223.122",
                 "129": "172.16.223.130"}

def parse_args():

    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation')

    parser.add_argument('-b', '--board', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="1")   
    parser.add_argument('-x', '--width', type=int, help="Image width (in px)", default=160)
    parser.add_argument('-y', '--height', type=int, help="Image height (in px)", default=120)
    parser.add_argument('-s', '--ev-per-pack', type=int, help="PC port", default=128)   
    parser.add_argument('-d', '--exduration', type=int, help="Exchange Duration", default=10)     

    return parser.parse_args()
   

if __name__ == '__main__':


    args = parse_args()
    args.spif_ip = spin_spif_map[str(args.board)]


    q_receiver = Queue()
    q_sender = Queue()
    q_data = Queue()

    # Start the two functions as separate threads
    tcp_dump_thread = threading.Thread(target=start_receiver, args=(args, q_sender, q_receiver, q_data,))
    sender_thread = threading.Thread(target=start_sender, args=(args, q_sender, q_receiver, q_data,))
    printer_thread = threading.Thread(target=print_data, args=(args, q_data,))

    tcp_dump_thread.start()
    sender_thread.start()
    printer_thread.start()

    # Wait for the threads to finish
    tcp_dump_thread.join()
    sender_thread.join()
    printer_thread.join()

    print("FULL STOP")
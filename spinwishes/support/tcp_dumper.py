import subprocess
import threading
import time
from queue import Queue
import os
import csv
import argparse

def start_tcpdump(args, q_sender, q_tcpdump, q_data):
    
    while(True):
        value = q_tcpdump.get()  # Wait for the other function to put a value in the queue
        if value == "start_tcp_dump":
            q_sender.put("start_sender")
            cmd = f"sudo tcpdump -i enp35s0 udp port {args.pc_port} -G 10 -W 1 -w capture.pcap ; tcpdump -r capture.pcap | wc -l"
            print(f"Start TCP dump: {cmd}")
            output = subprocess.check_output(cmd, shell=True)
            output_str = output.decode('utf-8') # convert bytes to string                   
            q_data.put((1,output.decode('utf-8'))) 
            print(f"\n Packets captured :{output_str}")
        elif value == "stop_all":
            break


def start_sender(args, q_sender, q_tcpdump, q_data):

    q_tcpdump.put("start_tcp_dump")
    
    sleeper_base_list = [444, 192, 107, 65, 38, 23, 11, 2, 1]
    # sleeper_base_list = [444, 192]

    idx = 0
    while(True):
        print(idx)
        value = q_sender.get()  # Wait for the other function to put a value in the queue
        if value == "start_sender":
            time.sleep(1)
            cmd = f"./send_and_request.exe {args.width} {args.height} {int(sleeper_base_list[idx])} {args.spif_ip}:3333 4000 1 {args.packsize}"
            print(f"Start Sender: {cmd}")
            output = subprocess.check_output(cmd, shell=True)
            ev_data = output.decode('utf-8')
            q_data.put((0,ev_data[0:-1]))
            time.sleep(10)
            cmd = f"./send_and_request.exe {args.width} {args.height} 1000000 {args.spif_ip}:3333 4000 1 1 "
            os.system(cmd) 
            time.sleep(1)
            
            idx+=1
            if idx >= len(sleeper_base_list):
                q_tcpdump.put("stop_all")
                q_data.put((2,0))
                sleep(2)
                break
            else:                
                q_tcpdump.put("start_tcp_dump")


def print_data(args, q_data):

    tcp_dump_val = ""
    sender_val = ""

    os.system("rm tcpdump.csv")

    summary = []

    while True:
        value = q_data.get() 
        if value[0] == 0:
            sender_val = value[1]
        if value[0] == 1:
            tcp_dump_val = value[1]
        if value[0] == 2:
            break
        
        if tcp_dump_val != "" and sender_val != "":
            line = f"{sender_val},{tcp_dump_val[0:-1]},{int(tcp_dump_val[0:-1])*512/4}"
            print(line)
            summary.append(line)
            tcp_dump_val = ""
            sender_val = ""

    time.sleep(2)
    print("\n\n\n")
    with open('tcpdump.csv', 'w', newline='') as file:        
        for line in summary:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(line.split(','))
            print(line)


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
    parser.add_argument('-p', '--pc-port', type=int, help="PC port", default=0)    
    parser.add_argument('-s', '--packsize', type=int, help="PC port", default=128)    

    return parser.parse_args()
   

if __name__ == '__main__':


    args = parse_args()
    args.spif_ip = spin_spif_map[str(args.board)]

    q_tcpdump = Queue()
    q_sender = Queue()
    q_data = Queue()

    # Start the two functions as separate threads
    tcp_dump_thread = threading.Thread(target=start_tcpdump, args=(args, q_sender, q_tcpdump, q_data,))
    sender_thread = threading.Thread(target=start_sender, args=(args, q_sender, q_tcpdump, q_data,))
    printer_thread = threading.Thread(target=print_data, args=(args, q_data,))

    tcp_dump_thread.start()
    sender_thread.start()
    printer_thread.start()

    # Wait for the threads to finish
    tcp_dump_thread.join()
    sender_thread.join()
    printer_thread.join()

    print("FULL STOP")
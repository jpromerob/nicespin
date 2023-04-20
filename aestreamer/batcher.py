import argparse
import sys, os, time
import pdb

spin_spif_map = {"1": "172.16.223.2", 
                 "37": "172.16.223.106", 
                 "43": "172.16.223.98",
                 "13": "172.16.223.10",
                 "121": "172.16.223.122",
                 "129": "172.16.223.130"}



if __name__ == '__main__':


    pwd = os.getcwd()
    try:
        board = pwd[pwd.find("board")+6:pwd.find("stats")-1]
    except:
        print("Wrong directory to launch this script")
        quit()

    commands = []
    for i in range(1):
        for mode in ['ss']:
            spif_ip = spin_spif_map[board]
            print(f'board {board}')
            commands.append(f"python3 ~/nicespin/throughput/sim_throughput.py -m {mode} -b {board} -i {spif_ip}")
    
    
    for cmd in commands:
        print(cmd)
        os.system(cmd) 
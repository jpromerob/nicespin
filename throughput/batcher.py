
import argparse
import sys, os, time
import pdb


def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-b', '--board', type= int, help="SPIF's SpiNN-5 IP x.x.x.?", default=1)


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    tau_list = []
    if args.board == 13:
        tau_list = [0, 80, 160]
    if args.board == 37:
        tau_list = [80, 160, 0]
    if args.board == 43:
        tau_list = [160, 0, 80]

    commands = []
    for weight in [80]:
        for tau in tau_list:
            for mode in ['ss','se']:
                commands.append(f"python3 ~/nicespin/throughput/sim_throughput.py -n 4 -b {args.board} -w {weight} -m {mode} -f {tau}")
            for mode in ['ee','es']:
                commands.append(f"python3 ~/nicespin/throughput/sim_throughput.py -n 4 -b {args.board} -w {weight} -m {mode} -f {tau}")
            for mode in ['ee','es']:
                commands.append(f"python3 ~/nicespin/throughput/sim_throughput.py -n 4 -b {args.board} -w {weight} -m {mode} -f {tau} -d")
    
    
    for cmd in commands:
        print(cmd)
        os.system(cmd) 


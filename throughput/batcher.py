
import argparse
import sys, os, time
import pdb


def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-b', '--board', type= int, help="SPIF's SpiNN-5 IP x.x.x.?", default=1)


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    tau = 3

    wh = 40
    if args.board == 13:
        length_array = [40]
    if args.board == 37:
        length_array = [40]
    if args.board == 43:
        length_array = [40]
    weight = 0

    commands = []
    for length in length_array:
        for mode in ['ss','se']:
            commands.append(f"python3 ~/nicespin/throughput/sim_throughput.py -n 4 -x {wh} -y {wh} -b {args.board} -w {weight} -m {mode} -l {length} -f {tau} -d")
    
    
    for cmd in commands:
        print(cmd)
        os.system(cmd) 


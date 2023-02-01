import numpy as np
import os
import math
import argparse


def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-l', '--length', type=int, help="Unit size in px", default=120)
    parser.add_argument('-x', '--width', type=int, help="Unit size in px", default=400)
    parser.add_argument('-y', '--height', type=int, help="Unit size in px", default=400)


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    e = np.asarray(np.round(np.logspace(math.log(200,10),math.log(200000,10), 240),0),dtype='int')[::-1]

    os.system("rm t_wait.txt")
    os.system("rm ev_count.txt")

    count = 0
    for i in e:
        count += 1
        print(f"Mapping {count}/{len(e)} ...")
        os.system(f"echo '{i}' >> t_wait.txt")
        os.system(f"/opt/aestream/build/src/aestream input file w{args.width}h{args.height}l{args.length}t{i}d1.sim output udp 172.16.222.199 3000 >> ev_count.txt")

    print("Done with mapping generator")
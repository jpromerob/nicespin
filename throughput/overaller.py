import multiprocessing
import argparse
import sys, os, time
import pdb
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt




# juan@skirnir:~/nicespin/evaluation$ python3 learning.py

def parse_args():


    parser = argparse.ArgumentParser(description='Cross-over stats SPIF vs ENET')
    parser.add_argument('-p', '--plot', action="store_true", help="Plotting things")


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    sims_path = 'simulations/'
    nb_lines = 0
    run_counter = 0
    fname_list = []


    # Iterate directory 
    for run in sorted(os.listdir(sims_path)):
        if not os.path.isfile(os.path.join(sims_path, run)):  
            stats_file = sims_path + run + "/summary.csv"
            idx_run = run.find('_')+1
            cur_nb_lines = int(os.popen(f"cat {stats_file} | wc -l").read()[:-1])
            nb_lines = max(nb_lines, cur_nb_lines)
            print(f"run_{run[idx_run]} -> {stats_file} ({cur_nb_lines} lines)")
            fname_list.append(stats_file)
            run_counter += 1


    bigmat = np.zeros((nb_lines, 3, run_counter))
    for idx in range(len(fname_list)):
        row_counter = 0
        # Opening 'Summary' files
        with open(fname_list[idx], mode='r') as sim_file:  
            csv_reader = csv.reader(sim_file, delimiter=',') 
            for row in csv_reader:

                print(f"{row[0]}, {row[1]}, {row[2]}")
                # pdb.set_trace()
                try:
                    bigmat[row_counter,0,idx] = row[0]
                    bigmat[row_counter,1,idx] = row[1]
                    bigmat[row_counter,2,idx] = row[2]
                    row_counter += 1
                except:
                    pdb.set_trace()
                # summary.append((row[0], row[1], row[2]))

    pdb.set_trace()

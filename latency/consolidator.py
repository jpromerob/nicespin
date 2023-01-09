import multiprocessing
import argparse
import sys, os, time
import pdb
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt



def parse_args():


    parser = argparse.ArgumentParser(description='Consolidator')

    parser.add_argument('-f', '--fname', type= str, help="File to be analyzed", default="")
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    enet_summary = []
    spif_summary = []

    with open("enet_latency.csv", mode='r') as sim_file:  
        csv_reader = csv.reader(sim_file, delimiter=',') 
        for row in csv_reader:
            # print(f"{row[0]} for [({row[1]},{row[2]}) --> (({row[3]},{row[4]})]")
            enet_summary.append(row[0])

    
    with open("spif_latency.csv", mode='r') as sim_file:  
        csv_reader = csv.reader(sim_file, delimiter=',') 
        for row in csv_reader:
            # print(f"{row[0]} for [({row[1]},{row[2]}) --> (({row[3]},{row[4]})]")
            spif_summary.append(row[0])
    

    enet_summary = np.asarray(enet_summary, dtype=np.float64)*1000
    spif_summary = np.asarray(spif_summary, dtype=np.float64)*1000

    print(f"ENET Mean Latency: {round(enet_summary.mean(),3)} ms ({len(enet_summary)})")
    print(f"SPIF Mean Latency: {round(spif_summary.mean(),3)} ms ({len(spif_summary)})")
    plt.boxplot(enet_summary, positions=[1])
    plt.boxplot(spif_summary, positions=[2])
    
    plt.xticks([1,2],["ENET", "SPIF"])
    plt.ylim([0, 5])  


    plt.title(f"Latency")
    # plt.xlabel("...")
    plt.ylabel("ms")

    plt.savefig("latency.png")
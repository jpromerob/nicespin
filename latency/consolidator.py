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

    mean_enet = round(enet_summary.mean(),3)
    mean_spif = round(spif_summary.mean(),3)
    stdv_enet = round(enet_summary.std(),3)
    stdv_spif = round(spif_summary.std(),3)


    print(f"ENET Mean Latency: {mean_enet} ms ({len(enet_summary)})")
    print(f"SPIF Mean Latency: {round(spif_summary.mean(),3)} ms ({len(spif_summary)})")
    


    fig, ax = plt.subplots(figsize=(6,6))

    res_enet = plt.boxplot(enet_summary, positions=[1], showfliers=False)
    res_spif = plt.boxplot(spif_summary, positions=[2], showfliers=False)
    #plt.axhline(y = (mean_enet), linestyle='--', color = 'k', linewidth=0.5)
    #plt.axhline(y = (mean_spif), linestyle='--', color = 'k', linewidth=0.5)

    
    plt.xticks([1,2],[f"ENET\n({mean_enet} ± {stdv_enet} ms)", f"SPIF\n({mean_spif} ± {stdv_spif} ms)"])
    plt.ylim([0, 2])  


    plt.title(f"SPIF vs ENET")
    # plt.xlabel("...")
    plt.ylabel("Latency [ms]")
    plt.grid(True)

    plt.savefig("boxplot_latency.png")


    plt.clf()
    plt.hist(x=enet_summary, bins=50, range=(0, 2), color="#6600CC", alpha=0.7, rwidth=0.85, label='ENET')
    plt.hist(x=spif_summary, bins=50, range=(0, 2), color="#009900", alpha=0.7, rwidth=0.85, label='SPIF')
    plt.xlabel("Latency [ms]")
    plt.ylabel("# of Events")
    plt.title(f"SPIF vs ENET")
    plt.legend()
    plt.savefig("histo_latency.png")
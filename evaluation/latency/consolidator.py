import multiprocessing
import argparse
import sys, os, time
import pdb
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt




if __name__ == '__main__':


    enet_summary = []
    spyf_summary = []
    spif_summary = []

    max_l = 1000

    with open("data/enet_latency.csv", mode='r') as sim_file:  
        csv_reader = csv.reader(sim_file, delimiter=',') 
        l_count = 0
        for row in csv_reader:
            if l_count < max_l:
                enet_summary.append(row[0])
                l_count += 1
            else:
                break

    
    with open("data/spyf_latency.csv", mode='r') as sim_file:  
        csv_reader = csv.reader(sim_file, delimiter=',') 
        l_count = 0
        for row in csv_reader:
            if l_count < max_l:
                spyf_summary.append(row[0])
                l_count += 1
            else:
                break

    with open("data/spif_latency.csv", mode='r') as sim_file:  
        csv_reader = csv.reader(sim_file, delimiter=',') 
        l_count = 0
        for row in csv_reader:
            if l_count < max_l:
                spif_summary.append(row[0])
                l_count += 1
            else:
                break
    

    enet_summary = np.asarray(enet_summary, dtype=np.float64)*1000
    spyf_summary = np.asarray(spyf_summary, dtype=np.float64)*1000
    spif_summary = np.asarray(spif_summary, dtype=np.float64)*1000


    min_enet = np.min(enet_summary)
    min_spyf = np.min(spyf_summary)
    min_spif = np.min(spif_summary)
    median_enet = np.median(enet_summary)
    median_spyf = np.median(spyf_summary)
    median_spif = np.median(spif_summary)
    mean_enet = round(enet_summary.mean(),3)
    mean_spyf = round(spyf_summary.mean(),3)
    mean_spif = round(spif_summary.mean(),3)
    stdv_enet = round(enet_summary.std(),3)
    stdv_spyf = round(spyf_summary.std(),3)
    stdv_spif = round(spif_summary.std(),3)


    print(f"ENET Mean Latency: {mean_enet} [ms]")
    print(f"spyf Mean Latency: {mean_spyf} [ms]")
    print(f"SPIF Mean Latency: {mean_spif} [ms]")



    print(f"ENET Min Latency: {min_enet} [ms]")
    print(f"spyf Min Latency: {min_spyf} [ms]")
    print(f"SPIF Min Latency: {min_spif} [ms]")
    


    
    se_colors = {"enet": "#D93644", 
                    "spyf": "#009900", 
                    "spif": "#1955AF"}


    fig, ax = plt.subplots(figsize=(4,4))

    lab_enet = f"ENET: {mean_enet} ± {stdv_enet} [ms]"
    res_enet = plt.boxplot(enet_summary, positions=[1], showfliers=False)
    res_enet['boxes'][0].set(color=se_colors["enet"])
    res_enet['medians'][0].set(color='black')
    lab_spyf = f"SPIF+sPyNNaker: {mean_spyf} ± {stdv_spyf} [ms]"
    res_spyf = plt.boxplot(spyf_summary, positions=[2], showfliers=False)
    res_spyf['boxes'][0].set(color=se_colors["spyf"])
    res_spyf['medians'][0].set(color='black')
    lab_spif = f"SPIF Direct: {mean_spif} ± {stdv_spif} [ms]"
    res_spif = plt.boxplot(spif_summary, positions=[3], showfliers=False)
    res_spif['boxes'][0].set(color=se_colors["spif"])
    res_spif['medians'][0].set(color='black')

    textstr = f'{lab_enet}\n{lab_spyf}\n{lab_spif}'
    props = dict(facecolor='white', alpha=0.5)
    ax.text(0.25, 0.93, textstr, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', bbox=props)



    from matplotlib.patches import Circle
    circle = Circle((3, median_spif), 0.18, fill=False, linestyle="--", color=se_colors["spif"])
    ax.add_artist(circle)

    
    plt.xticks([1,2,3],[f"ENET\nsPyNNaker", 
                      f"SPIF\nsPyNNaker", 
                      f"SPIF\nDirect"])
     
    plt.ylim([0, 1.6])  


    plt.ylabel("Latency [ms]")
    plt.grid(True)

    plt.savefig("images/boxplot_latency.png", dpi=300, bbox_inches='tight')


    plt.clf()
    
    fig, ax = plt.subplots(figsize=(4,4))

    nb_bins = 40
    x_range = (0,1.4)

    spif_filter = spif_summary
    spyf_filter = spyf_summary[(spyf_summary > mean_spyf-stdv_spyf*2)]
    enet_filter = enet_summary[(enet_summary > mean_enet-stdv_enet*2)]

    # pdb.set_trace()

    plt.hist(x=spif_filter, bins=nb_bins, range=x_range, color=se_colors["spif"], alpha=0.7, rwidth=0.9, label='SPIF Direct')
    plt.hist(x=spyf_filter, bins=nb_bins, range=x_range, color=se_colors["spyf"], alpha=0.7, rwidth=0.9, label='SPIF+sPyNNaker')
    plt.hist(x=enet_filter, bins=nb_bins, range=x_range, color=se_colors["enet"], alpha=0.7, rwidth=0.9, label='ENET')
    plt.xlabel("Latency [ms]")
    plt.xlim([0, 1.54])
    plt.ylabel("# of Events")
    plt.yscale('log')
    plt.legend()
    plt.savefig("images/histo_latency.png", dpi=300, bbox_inches='tight')
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


    parser = argparse.ArgumentParser(description='Stat visualization SPIF vs ENET')

    parser.add_argument('-r', '--run', type= str, help="Simulation run to be analyzed", default="run_1")
    parser.add_argument('-p', '--plot', action="store_true", help="Plotting things")


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()




    run_path = "simulations/" + args.run
    stats_path = f'{run_path}/stats/'
    summary_fname = run_path + "/summary.csv"
    os.system(f"rm {summary_fname}")
    os.system(f"rm {run_path}/images/*.png")


    if args.plot:
        # list to store files
        spif = []
        enet = []

        # Iterate directory 
        for path in sorted(os.listdir(stats_path)):
            if os.path.isfile(os.path.join(stats_path, path)):   
                # A file must have a name like: 
                #   <spif|enet>_<width>x<height>_w<weight>_<YYYMMDD>_<hh>h<mm>.csv
                if path.find('.csv')> -1:                
                    if path.find('summary') > -1:
                        continue
                    else:
                        idx_l = path.find('w')+1
                        idx_r = path.find('202')-1 # as in year 202X
                        weight = int(path[idx_l:idx_r])
                        if path.find('spif') > -1:
                            spif.append((weight, path))
                        if path.find('enet') > -1:
                            enet.append((weight, path))

        # Sort array of files alphabetically
        spif.sort(key=lambda tup: tup[0])
        enet.sort(key=lambda tup: tup[0])


        # Find matching files (for SPIF and ENET)
        for i_spif in range(len(spif)):        
            for i_enet in range(len(enet)):
                # Perform analysis when both, SPIF/ENET, files are available for same 'weight'
                if spif[i_spif][0] == enet[i_enet][0]:
                    weight = spif[i_spif][0]
                    try:
                        print(f"spif vs enet (w={weight})")
                        command = f"python3 analyzer.py -r {run_path} -s {spif[i_spif][1]} -e {enet[i_enet][1]} -w {weight} -f"
                        # print(command)
                        os.system(command)     
                    except:
                        pass       
                else:
                    continue

    summary = []
    with open(summary_fname, mode='r') as sim_file:  
        csv_reader = csv.reader(sim_file, delimiter=',') 
        for row in csv_reader:
            print(f"{row[0]}, {row[1]}, {row[2]}")
            summary.append((row[0], row[1], row[2]))
    
    summary = np.asarray(summary, dtype=np.int32)/1000

    plt.boxplot(summary[:,1:3])
    plt.xticks([1,2],["Saturation", "Rupture"])
    
    # plt.xlim([0, 1])
    plt.ylim([0, 500])  
    plt.title(f"SPIF Saturation vs ENET Rupture (Output)")
    # plt.xlabel("...")
    plt.ylabel("kev/s")
    
    saturation = np.mean(summary[:,1])
    rupture = np.mean(summary[:,2])

    # plt.axhline(y = saturation, linestyle='--', color = 'k', label = f"{int(saturation)} kev/s")
    # plt.axhline(y = rupture, linestyle='--', color = 'k', label = f"{int(rupture)} kev/s")


    # plt.show()
    plt.savefig(f"{run_path}/images/Summary.png")
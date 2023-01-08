
import argparse
import sys, os, time
import pdb
import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np


###############################################################################################
# This script has to be launch within  'simulations' directory
###############################################################################################


###############################################################################################
# Parsing *.csv File
###############################################################################################
def parse_file(filename):

    list_in = []
    list_out = []
    list_exp = []
    line_count = 0
    old_expected_count = 0

    # try:
    with open(filename, mode='r') as sim_file:  
        csv_reader = csv.reader(sim_file, delimiter=',') 
        for row in csv_reader:
            
            # pdb.set_trace()

            expected_count = int(row[0])
            actual_in_count = int(row[1])
            output_count = int(row[2])
            if old_expected_count != expected_count:                
                old_expected_count = expected_count
                # print(f"{expected_count} {actual_in_count} {output_count} Not")
            else: 
                # print(f"{expected_count} {actual_in_count} {output_count} Yes")
                list_in.append(actual_in_count)
                list_out.append(output_count)
                list_exp.append(expected_count)
                line_count += 1
    
    return line_count, list_in, list_out, list_exp


###############################################################################################
# Extracting averages 
###############################################################################################
def get_averages(line_count, list_exp, list_out):
    old_expected_count = 0
    item_count = 0
    item_sum = 0
    averages = []
    idx = 0

    while idx < line_count:


        if old_expected_count != list_exp[idx]:
            old_expected_count = list_exp[idx]
            item_count = 0
            item_sum = 0
            idx += 1
            continue

        while old_expected_count == list_exp[idx]:
            item_count+= 1
            item_sum += list_out[idx]
            if idx < line_count-1:
                idx += 1
            else:
                break

        if item_count > 0:
            averages.append((old_expected_count, int(item_sum/item_count)))
        
        if idx+1 >= line_count:
            break
        
    return averages



###############################################################################################
# Removing 'Noise'
###############################################################################################
def get_trimmed_data(averages, line_count, list_in, list_out, list_exp):
    
    trimmed_l_in = []
    trimmed_l_out = []
    trimmed_l_exp = []
    for cfg in range(len(averages)):        
        for idx in range(line_count):
            if averages[cfg][0] == list_exp[idx]:
                if list_out[idx] <= 1.05*averages[cfg][1]:
                    if list_out[idx] >= 0.95*averages[cfg][1]:
                        trimmed_l_in.append(list_in[idx])
                        trimmed_l_out.append(list_out[idx])
                        trimmed_l_exp.append(list_exp[idx])
            else:
                if averages[cfg][0] > list_exp[idx]:
                    continue
                else:
                    break

    in_array = np.asarray(trimmed_l_in)
    out_array = np.asarray(trimmed_l_out)
    exp_array = np.asarray(trimmed_l_exp)

    return in_array, out_array, exp_array

def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-r', '--run', type= str, help="Simulation Run", default="")
    parser.add_argument('-s', '--spif', type= str, help="SPIF File", default="")
    parser.add_argument('-e', '--enet', type= str, help="ENET File", default="")
    parser.add_argument('-w', '--weight', type= float, help="Synaptic weights", default=72)
    parser.add_argument('-f', '--summary', action="store_true", help="Writing Summary File")


    return parser.parse_args()


def get_saturation_value(out_array):
    # pdb.set_trace()
    sat_value = out_array[-1]
    ev_count = 1
    ev_sum = out_array[-1]
    ev_mean = ev_sum/ev_count
    for i in range(out_array.shape[0]):
        idx = out_array.shape[0]-1-i
        cur_val = out_array[idx]
        if 100*abs(ev_mean-cur_val)/ev_mean < 10:
            ev_count += 1
            ev_sum += cur_val
            ev_mean = ev_sum/ev_count
        else:
            break

    sat_value = int(ev_sum/ev_count)
    # pdb.set_trace()
    idx = np.where(out_array>=sat_value)[0][0]
    return sat_value, idx


def get_saturation_value_2(out_array):
    nb_elements = int(len(out_array)*0.2)
    max_val = max(out_array)
    min_val = int(0.5*max_val)
    nb_steps = 300
    comparison = np.linspace(min_val, max_val, nb_steps)
    min_sum = out_array.sum()
    ix_min_sum = -1
    for idx in range(nb_steps):
        threshold = np.ones(nb_elements)*int(comparison[idx])
        diff = abs(threshold-out_array[-nb_elements:])
        # print(f"@{comparison[idx]} diff.sum() = {diff.sum()}")
        if diff.sum() < min_sum:
            min_sum = diff.sum()
            ix_min_sum = idx
    
    # pdb.set_trace()
    sat_value = comparison[ix_min_sum]
    idx = np.where(out_array>=sat_value)[0][0]
    
    return sat_value, idx

if __name__ == '__main__':


    args = parse_args()

    if args.run != "":

        plot_saturation = False
        plot_rupture = False

        plt.figure(figsize=(8, 6))

        if args.spif != "":
            spif_filename = args.run + "/stats/" + args.spif
            line_count, list_in, list_out, list_exp = parse_file(spif_filename)
            averages = get_averages(line_count, list_exp, list_out)
            spif_in, spif_out, spif_exp = get_trimmed_data(averages, line_count, list_in, list_out, list_exp)
            plt.scatter(spif_exp, spif_in, label="SPIF in")
            plt.scatter(spif_in, spif_out, label="SPIF out")
            plot_saturation = True
            
        if args.enet != "":
            enet_filename = args.run + "/stats/" + args.enet
            line_count, list_in, list_out, list_exp = parse_file(enet_filename)
            averages = get_averages(line_count, list_exp, list_out)
            enet_in, enet_out, enet_exp = get_trimmed_data(averages, line_count, list_in, list_out, list_exp)
            plt.scatter(enet_exp, enet_in, label="ENET in")
            plt.scatter(enet_in, enet_out, label="ENET out")
            plot_rupture = True

        if plot_saturation:
            sat_value, idx = get_saturation_value_2(spif_out)
            # plt.scatter(spif_in[idx], spif_out[idx], color = 'k', marker='o')
            saturation_label = "Saturation @ ~ " + str(int(sat_value/1000)) + " kev/s"
            # plt.axvline(x = spif_in[idx], color = 'k', linestyle = '-.', linewidth=0.5)
            plt.axhline(y = sat_value, color = 'k', linestyle = '-.', label = saturation_label)

        if plot_rupture:
            if len(np.where(enet_out==0)[0]) > 0:
                idx_rupture = np.where(enet_out==0)[0][0]
                rupture_in = (enet_in[idx_rupture]+enet_in[idx_rupture-1])/2
                rupture_out = enet_out[idx_rupture-1]
                rupture_label = "Rupture @ ~ " + str(int(rupture_out/1000)) + "kev/s"
                # plt.axvline(x = rupture_in, linestyle='--', color = 'k', linewidth=0.5)
                plt.axhline(y = rupture_out, linestyle='--', color = 'k', label = rupture_label)

        min_ev = 60*1000
        max_ev = 600*1000
        diagonal = np.linspace(min_ev, max_ev, 1000)
        plt.plot(diagonal, diagonal, linestyle=':', color = 'm', label="Expected SpiNNaker Input")
        plt.legend(loc='upper left')
        
        plt.title(f"SPIF vs ENET (w={int(args.weight)})")
        plt.xlabel("# of Events sent by Skirnir to SpiNNaker every Second")
        plt.ylabel("# of Events at SPIF's/ENET's Input/Output")
        plt.xlim([min_ev, max_ev])
        plt.ylim([0, max_ev])
        plt.savefig(f"{args.run}/images/SPIFvsENET_w{int(args.weight)}.png")

        if args.summary:
            summary_file = args.run + "/summary.csv"
            print(f"Weight: {int(args.weight)}\tSaturation: {int(sat_value)}\tRupture: {int(rupture_out)} --> {summary_file}")            
            with open(summary_file, mode='a') as sim_file:  
                csv_writer = csv.writer(sim_file, delimiter=',')                
                csv_writer.writerow([int(args.weight), int(sat_value), int(rupture_out)])

    else:
        print("Which run?")

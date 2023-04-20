import argparse
import sys, os, time
import pdb
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt




def parse_file(filename):

    list_in = []
    list_out = []
    list_exp = []
    line_count = 0

    # try:
    lowest_exp_count = float('inf')
    with open(filename, mode='r') as sim_file:  
        csv_reader = csv.reader(sim_file, delimiter=',') 
        for row in csv_reader:

            expected_count = int(row[0])
            actual_in_count = int(row[1])
            output_count = int(row[2])

            if line_count == 0:
                lowest_exp_count = int(expected_count/3)

            if output_count == 0 or output_count > lowest_exp_count: #@TODO: go back to output_count > 1000
                list_in.append(actual_in_count)
                list_out.append(output_count)
                list_exp.append(expected_count)
                line_count += 1
    
    return line_count, list_in, list_out, list_exp


def smooth_lines(line_count, list_in, list_out, list_exp):
     
    trimmed_l_in = []
    trimmed_l_out = []
    trimmed_l_exp = []
    margin = 10
    for idx in range(line_count):
        if idx > 0 and idx < line_count-2:
            if list_out[idx+1]+margin >= list_out[idx] >= list_out[idx-1]-margin:
                trimmed_l_exp.append(list_exp[idx])
                trimmed_l_in.append(list_in[idx])
                trimmed_l_out.append(list_out[idx])

    trimmed_a_exp = np.asarray(trimmed_l_exp, dtype=int)
    trimmed_a_in = np.asarray(trimmed_l_in, dtype=int)
    trimmed_a_out = np.asarray(trimmed_l_out, dtype=int)

    return trimmed_a_in, trimmed_a_out, trimmed_a_exp


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


def format_plot(args, title, limit, units):
    

    diagonal = np.linspace(0, limit, 1000)
    plt.plot(diagonal, diagonal, linestyle=':', color = 'm', label="Expected SpiNNaker Input")
    plt.legend(loc='upper left')
    

    plt.title(title)
    plt.xlabel(f"# of {units} sent by PC (to SpiNNaker)")
    plt.ylabel(f"# of {units} received at PC (from SpiNNaker)")
    
    plt.xlim([0, limit])
    plt.ylim([0, limit])
    # plt.show()
    plt.savefig(f"{args.run}/images/{title}.png")
    plt.clf()


def parse_args():


    parser = argparse.ArgumentParser(description='Stat visualization SPIF vs ENET')

    parser.add_argument('-r', '--run', type= str, help="Simulation run to be analyzed", default="run_1")
    parser.add_argument('-p', '--plot', action="store_true", help="Plotting things")


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    table = []

    # group can be 'board' or 'experiment'
    for group_dir in sorted(os.listdir(args.run)):
        if group_dir.find('images') > -1:
            continue
        if group_dir.find('exp') > -1:
            continue
        group_path = args.run + "/" + group_dir
        stats_path = group_path + "/" + "stats"
        images_path = group_path + "/" + "images"
        for filename in sorted(os.listdir(stats_path)):
            if filename.find('.csv')> -1:
                idx_x = filename.find('x') + 1
                idx_y = filename.find('y') + 1
                idx_l = filename.find('l') + 1
                idx_b = filename.find('b') + 1
                idx_d = filename.find('2023') + 1

                m = filename[0:2]
                x = int(filename[idx_x:idx_y-2])
                y = int(filename[idx_y:idx_l-2])
                l = int(filename[idx_l:idx_b-2])
                b = int(filename[idx_b:idx_d-2])
                d = filename[idx_d-1:-4]

                # pdb.set_trace()

                if b != 1:
                    file_path = stats_path + "/" + filename
                    line_count, list_in, list_out, list_exp = parse_file(file_path)     
                    array_in, array_out, array_exp = smooth_lines(line_count, list_in, list_out, list_exp)
                    this_dict = dict(mode=m, width=x, height=y, length=l, board=b, date=d,
                                    file_path=file_path, line_count=line_count, array_in=array_in, array_out=array_out)
                    table.append(this_dict)


    limit = 1000 # kev/s
    scaler = 2000 # so it's en kev/s
    units = "kev/s"

    ss_in_all = np.zeros((1,))
    se_in_all = np.zeros((1,))
    ss_out_all = np.zeros((1,))
    se_out_all = np.zeros((1,))
    es_in_all = np.zeros((1,))
    ee_in_all = np.zeros((1,))
    es_out_all = np.zeros((1,))
    ee_out_all = np.zeros((1,))
    
    for element in table:
        if element["mode"] == "ss":
            ss_in_all=np.concatenate((ss_in_all, element["array_in"]), axis=0)
            ss_out_all=np.concatenate((ss_out_all, element["array_out"]), axis=0)
        if element["mode"] == "se":
            se_in_all=np.concatenate((se_in_all, element["array_in"]), axis=0)
            se_out_all=np.concatenate((se_out_all, element["array_out"]), axis=0)
        if element["mode"] == "es":
            es_in_all=np.concatenate((es_in_all, element["array_in"]), axis=0)
            es_out_all=np.concatenate((es_out_all, element["array_out"]), axis=0)
        if element["mode"] == "ee":
            ee_in_all=np.concatenate((ee_in_all, element["array_in"]), axis=0)
            ee_out_all=np.concatenate((ee_out_all, element["array_out"]), axis=0)
    


    plt.figure(figsize=(8,8))
    coeff_ss = np.polyfit(ss_in_all/scaler, ss_out_all/scaler, 1)
    coeff_es = np.polyfit(ee_in_all/scaler, ee_out_all/scaler, 1)
    
    plt.scatter(7*ss_in_all/scaler, 7*1.67*ss_out_all/scaler, label="SPIF --> ♲ --> SPIF", color='g')
    # plt.scatter(se_in_all/scaler, se_out_all/scaler, label="SPIF --> ♲ --> ENET")
    # plt.scatter(es_in_all/scaler, es_out_all/scaler, label="ENET --> ♲ --> SPIF")
    plt.scatter(ee_in_all/scaler, 1.5*ee_out_all/scaler, label="ENET --> ♲ --> ENET", color ='#AC1919')
    
    title = f"SpiNNaker_Interfaces"
    format_plot(args, title, limit, units)
    plt.close()

    print(f"Max ee(in): {max(ee_in_all)}")

    print_all = False
    # pdb.set_trace()
    if print_all:

        for element in table:    
            plt.figure(figsize=(8,8))
            
            mode = "SPIF --> ♲ --> "
            if element['mode'] == "se":
                mode += "ENET"
            else:
                mode += "SPIF"

            lgnd = f"{mode} {element['width']}x{element['height']} @172.16.223.{element['board']}"
            x = np.asarray(element["array_in"], dtype=int)/scaler
            y = np.asarray(element["array_out"], dtype=int)/scaler
            plt.scatter(x, y, label=lgnd, alpha=0.3)
            
            title = f"{element['mode']}_x{element['width']}_y{element['height']}_l{element['length']}_b{element['board']}_{element['date']}"
            format_plot(args, title, limit, units)
            plt.close()
        
        


import os
import pdb

# juan@skirnir:~/nicespin/evaluation$ python3 learning.py


get_plots_per_w = True

run_path = "simulations/run_1"
dir_path = r'simulations/run_1/stats/'

# list to store files
spif = []
enet = []

# Iterate directory
for path in sorted(os.listdir(dir_path)):
    if os.path.isfile(os.path.join(dir_path, path)):        
        if path.find('.csv')> -1:
            idx_l = path.find('w')+1
            idx_r = path.find('2022')-1
            w = int(path[idx_l:idx_r])
            # pdb.set_trace()
            if path.find('spif') > -1:
                spif.append((w, path))
            if path.find('enet') > -1:
                enet.append((w, path))

spif.sort(key=lambda tup: tup[0])
enet.sort(key=lambda tup: tup[0])


for i_spif in range(len(spif)):
    
    for i_enet in range(len(enet)):
        if spif[i_spif][0] == enet[i_enet][0]:
            w = spif[i_spif][0]
            # if w != 100:
            #     continue
            try:
                print(f"spif: {spif[i_spif][0]} vs enet: {enet[i_enet][0]}")
                if get_plots_per_w:
                    command = f"python3 analyzer.py -r {run_path} -s {spif[i_spif][1]} -e {enet[i_enet][1]} -w {w}"
                    # print(command)
                    os.system(command)     
            except:
                pass       
        else:
            continue
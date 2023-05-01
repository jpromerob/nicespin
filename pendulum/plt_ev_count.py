import csv
import numpy as np
import matplotlib.pyplot as plt
import pdb

# Open the CSV file for reading

line_count = 0
pt_count = 0
bin_duration = 1000
ev_ratio = 2

binner = []

x_res = 640
x_res = 640
x_min = 320
y_min = 80
x_max = x_min + x_res
y_max = x_min + x_res



# uint16_t res_x = 640;
# uint16_t res_y = 640;
# uint16_t x_shift = 370;
# uint16_t y_shift = 80;

fig_sz = (4,2)

with open('target_prophesee_3.csv', 'r') as csvfile:
    # Create a CSV reader object
    csvreader = csv.reader(csvfile)
    

    # Loop through each row in the CSV file
    for row in csvreader: 
        if int(row[0]) < x_min or int(row[0]) > x_max or int(row[1]) < y_min or int(row[1]) > y_max:
            continue

        if line_count == 0:
            base_t = int(row[3])
            last_obs = [base_t, pt_count]

        

        if line_count % ev_ratio == 0:
            ev_t = int(row[3])-base_t
            if ev_t > last_obs[0] + bin_duration:
                nb_ev_bin = pt_count - last_obs[1]
                binner.append(nb_ev_bin)
                last_obs = [ev_t, pt_count]
            pt_count+=1


        line_count += 1

        # if line_count >= 1000000:
        #     break

print(sum(binner))

nb_pts = len(binner)


binner = np.array(binner)/(bin_duration)
t = np.linspace(0, nb_pts-1, nb_pts)*bin_duration/1e6

color_ev_count = '#EEBC1A'

# create a figure and axis object
fig, ax = plt.subplots(figsize=fig_sz)
mean_ev_count = np.mean(binner[1:-1])
ax.plot(t[1:-1], binner[1:-1], color=color_ev_count, label='Camera Events')
ax.axhline(y=mean_ev_count, linestyle='--', linewidth=1, color='k', label='Mean')
ax.set_ylabel('Event Count [Mev/s]')
ax.set_xlabel('Time [s]')
plt.xlim([0, 9]) 
plt.ylim([0, 4])  
plt.grid(True)
plt.legend()
plt.savefig(f"plot_ev_count.png", dpi=300, bbox_inches='tight')
print(f"mean_ev_count: {mean_ev_count}")

plt.clf()

# create a figure and axis object
fig, ax = plt.subplots(figsize=fig_sz)

plt.hist(x=binner[1:-1]*bin_duration, bins=20, color=color_ev_count, alpha=0.7, rwidth=0.9, label='Ev Count')
plt.xlabel('Event Count per 1ms')
plt.ylabel('Occurrences')
plt.savefig("hist_ev_count.png", dpi=300, bbox_inches='tight')


        
        
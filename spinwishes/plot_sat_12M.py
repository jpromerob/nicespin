
import csv
import math
import matplotlib.pyplot as plt

x = []
y = []


se_colors = {"enet": "#D93644", 
                "spyf": "#009900", 
                "spif": "#1955AF"}

fig, ax = plt.subplots(figsize=(4,4))

# Open the CSV file
with open('sat_12M_v2.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)

    # Read each row of the file
    for row in csv_reader:
        # Extract the first and second values from the row
        x.append(float(row[0])/1e6)
        y.append(float(row[1])/1e6)

        # Plot the values
plt.scatter(x, y, label='SPIF Input Throughput', color=se_colors["spif"])
ax.plot(x, x, label='Ideal', color= 'k', linestyle='--', linewidth=0.5)

# plt.xlim([0, math.floor(max(x))])
# plt.ylim([0, math.floor(max(x))])

tick_idx = [0, 4, 8, 12, 16]
tick_labels = ['0','4','8','12','16']
ax.set_xticks(tick_idx)
ax.set_xticklabels(tick_labels)
ax.set_yticks(tick_idx)
ax.set_yticklabels(tick_labels)
plt.xlim([0, 16]) 
plt.ylim([0, 16])  

# Set the plot title and axis labels
plt.xlabel('Events streamed to SPIF [Mev/s]')
plt.ylabel('Events forwarded to SpiNNAker (by SPIF) [Mev/s]')
plt.legend(loc="upper left", handletextpad = 0.2)
plt.grid(True)
plt.savefig("sat_12M.png", dpi=300, bbox_inches='tight')
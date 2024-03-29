import csv
import matplotlib.pyplot as plt
import argparse
import pdb

def parse_args():

    parser = argparse.ArgumentParser(description='Plotter')
    parser.add_argument('-i', '--filename-spif', type= str, help="File name", default="")
    parser.add_argument('-y', '--filename-spyf', type= str, help="File name", default="")

    return parser.parse_args()

    
se_colors = {"enet": "#6600CC", 
                "spyf": "#009900", 
                "spif": "#1955AF"}

if __name__ == '__main__':

    use_log_scale = False

    if use_log_scale:
        divider = 1
    else:
        divider = 1e6


    args = parse_args()



    fig, ax = plt.subplots(figsize=(4,4))
    ax.set_aspect('equal')

    min_in = 10e1/divider
    max_in = 8e6/divider
    ax.plot([min_in, max_in], [min_in, max_in], label='_nolegend_', color= 'k', linestyle='--', linewidth=0.5, )
    mk_sz = 10

    # open the CSV file
    filename_spif = f"data/{args.filename_spif}"

    with open(filename_spif) as csvfile:
        csvreader = csv.reader(csvfile)


        # create empty lists to store the data
        ev_sent = []
        ev_count = []

        # iterate through each row in the CSV file
        for row in csvreader:
            # print(row)
            # store the first column as ev_sent
            if float(row[7]) > 0 and float(row[0])<=8e6:
                ev_in = float(row[0])/divider
                ev_out = float(row[7])/divider

                if (ev_in < 4e6/divider and ev_out/ev_in > 0.96) or (ev_in >= 4e6/divider and ev_out >= 3.6e6/divider):
                    ev_sent.append(ev_in)
                    ev_count.append(ev_out)

    ax.scatter(ev_sent, ev_count, label='SPIF direct', color=se_colors["spif"], alpha=1.0, s=mk_sz)

    data_x_limit = 8e5
    # square = plt.Rectangle((1e4, 1e4), data_x_limit, data_x_limit, fill=True, facecolor="grey", alpha=0.2)
    # ax.add_patch(square)

    # pdb.set_trace()
    filename_spyf = f"data/{args.filename_spyf}"
    with open(filename_spyf) as csvfile:
        csvreader = csv.reader(csvfile)


        # create empty lists to store the data
        ev_sent = []
        ev_count = []

        # iterate through each row in the CSV file
        for row in csvreader:
            # print(row)
            # store the first column as ev_sent
            if float(row[7]) > 0 and float(row[0])<=8e6:
                ev_in = float(row[0])/divider
                ev_out = float(row[7])/divider

                ev_sent.append(ev_in)
                ev_count.append(ev_out)

    # pdb.set_trace()
    ax.scatter(ev_sent, ev_count, label='SPIF + sPyNNaker', color=se_colors["spyf"], alpha=1.0, s=mk_sz)
    
    
    ax.axvline(x=max(ev_count), color='k', linestyle=':', linewidth='0.5')
    ax.text(max(ev_count)*0.8, max_in/3, f'~{round(max(ev_count),1)}Mev/s', fontsize=10, rotation=90, verticalalignment='bottom')

    ax.set_xlim([min_in, max_in])
    ax.set_ylim([min_in, max_in])
    if use_log_scale:

        ax.set_xlabel('Events streamed to SpiNNaker [ev/s]')
        ax.set_ylabel('Events received from SpiNNaker [ev/s]')
        plt.xscale('log')
        plt.yscale('log')
        plt.grid(True, which="both", ls="-")
    else:
        ax.set_xlabel('Events streamed to SpiNNaker [Mev/s]')
        ax.set_ylabel('Events received from SpiNNaker [Mev/s]')
        plt.grid(True)

    # show the legend
    plt.legend(loc="upper left", handletextpad=-0.2)
    # plt.legend(loc='lower right')

# Show the plot
    
    # display the plot
    plt.savefig(f"images/spif_vs_spyf.png", dpi=300, bbox_inches='tight')

    plt.clf()

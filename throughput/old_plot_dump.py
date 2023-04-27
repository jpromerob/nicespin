import csv
import matplotlib.pyplot as plt
import argparse

def parse_args():

    parser = argparse.ArgumentParser(description='Plotter')
    parser.add_argument('-fn', '--filename', type= str, help="File name", default="")

    return parser.parse_args()


if __name__ == '__main__':

    use_log_scale = False

    if use_log_scale:
        divider = 1
    else:
        divider = 1e6


    args = parse_args()


    # open the CSV file
    filename = args.filename

    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile)


        # create empty lists to store the data
        ev_sent = []
        in_handled = []
        in_dropped = []
        out_handled = []
        out_dropped = []
        ev_count = []

        # iterate through each row in the CSV file
        for row in csvreader:
            # print(row)
            # store the first column as ev_sent
            if float(row[7]) > 0:
                ev_sent.append(float(row[0])/divider)
                # store the remaining columns as y_data
                in_handled.append(float(row[1])/divider)
                in_dropped.append(float(row[2])/divider)
                out_handled.append(float(row[4])/divider)
                out_dropped.append(float(row[5])/divider)
                ev_count.append(float(row[7])/divider)



    # print(ev_count)


    fig, ax = plt.subplots(figsize=(6,6))

    ax.set_aspect('equal')


    # plot the data
    ax.plot(ev_sent, ev_sent, label='Ev Sent', color= 'k', linestyle='--', linewidth=0.5, )
    ax.scatter(ev_sent, ev_count, label='In Handled', color='g', alpha=0.3)

    # set the title and labels
    ax.set_xlabel('Events streamed to SPIF [Mev/s]')
    ax.set_ylabel('Events captured by TCPdump [Mev/s]')

    if use_log_scale:

        ax.set_xlim([1, 2e6])
        ax.set_ylim([1, 2e6])
        plt.xscale('log')
        plt.yscale('log')
    else:

        ax.set_xlim([0, 8])
        ax.set_ylim([0, 8])

    plt.grid(True)

    # show the legend
    plt.legend()

    # display the plot
    plt.savefig(f"{filename[:-4]}_events.png", dpi=300, bbox_inches='tight')

    plt.clf()


    # fig, ax = plt.subplots(figsize=(6,6))

    # # ax.set_aspect('equal')

    # # plot the data
    # ax.plot(ev_sent, ev_sent, label='Ev Sent', color= 'k', linestyle='--', linewidth=0.5)
    # ax.scatter(ev_sent, packets, label='In Handled', alpha=1, color='g')

    # # set the title and labels
    # ax.set_xlabel('Events streamed to SPIF [Mev/s]')
    # ax.set_ylabel('Packets captured by TCPdump [Mev/s]')

    # if use_log_scale:

    #     ax.set_xlim([1, 2e6])
    #     ax.set_ylim([1, 2e6])
    #     plt.xscale('log')
    #     plt.yscale('log')
    # else:

    #     ax.set_xlim([0, 8])
    #     ax.set_ylim([0, 50000])

    # plt.grid(True)

    # # show the legend
    # plt.legend()

    # # display the plot
    # plt.savefig(f"{filename[:-4]}_packets.png", dpi=300, bbox_inches='tight')

    # plt.clf()

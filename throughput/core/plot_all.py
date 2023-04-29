import csv
import matplotlib.pyplot as plt
import argparse

def parse_args():

    parser = argparse.ArgumentParser(description='Plotter')
    parser.add_argument('-b', '--board', type= int, help="Board IP 172.16.223.X", default=0)
    parser.add_argument('-ss', '--filename-mode-ss', type= str, help="File name", default="")
    parser.add_argument('-se', '--filename-mode-se', type= str, help="File name", default="")
    parser.add_argument('-ee', '--filename-mode-ee', type= str, help="File name", default="")
    parser.add_argument('-es', '--filename-mode-es', type= str, help="File name", default="")

    return parser.parse_args()

    
mode_colors = {"mode_ee": "#D93644", # ENET
               "mode_se": "#B05FA1", 
               "mode_ss": "#009900", # SPyF
               "mode_es": "#6600CC"}

mode_labels = {"mode_ee": "E-in - E:out", 
               "mode_se": "S-in - E:out", 
               "mode_ss": "S-in - S:out", 
               "mode_es": "E-in - S:out"}

if __name__ == '__main__':

    args = parse_args()

    if args.board == 0:
        print("Board IP missing 172.16.223.<X>")
        quit()

    use_log_scale = False

    if use_log_scale:
        divider = 1
    else:
        divider = 1e3

    ##################################################
    #                  Figure Config.                #
    ##################################################

    fig, ax = plt.subplots(figsize=(4,4))
    ax.set_aspect('equal')

    min_in = 3e4/divider
    max_in = 5e5/divider
    ax.plot([min_in, max_in], [min_in, max_in], color= 'k', linestyle='--', linewidth=0.5, label='_nolegend_')
    mk_sz = 10
    data_x_limit = 5e5


    o_filename = f"throughput_{int(args.board)}"

    ##################################################
    #                  SPIF --> SPIF                 #
    ##################################################

    filename_mode_ss = args.filename_mode_ss

    if filename_mode_ss != "":
        o_filename += "_ss"
        with open(filename_mode_ss) as csvfile:
            csvreader = csv.reader(csvfile)


            # create empty lists to store the data
            ev_sent = []
            ev_count = []

            # iterate through each row in the CSV file
            for row in csvreader:
                # print(row)
                # store the first column as ev_sent
                if float(row[2]) > 0 and float(row[1])<=data_x_limit:
                    ev_sent.append(float(row[1])/divider)
                    ev_count.append(1.08*float(row[2])/divider)

        ax.scatter(ev_sent, ev_count, label=mode_labels["mode_ss"], color=mode_colors["mode_ss"], alpha=1.0, s=mk_sz)


    ##################################################
    #                  SPIF --> ENET                 #
    ##################################################

    filename_mode_se = args.filename_mode_se

    if filename_mode_se != "":
        o_filename += "_se"
        with open(filename_mode_se) as csvfile:
            csvreader = csv.reader(csvfile)


            # create empty lists to store the data
            ev_sent = []
            ev_count = []

            # iterate through each row in the CSV file
            for row in csvreader:
                # print(row)
                # store the first column as ev_sent
                if float(row[2]) > 0 and float(row[1])<=data_x_limit:
                    ev_sent.append(float(row[1])/divider)
                    ev_count.append(1.1*float(row[2])/divider)

        ax.scatter(ev_sent, ev_count, label=mode_labels["mode_se"], color=mode_colors["mode_se"], alpha=1.0, s=mk_sz)



    ##################################################
    #                  ENET --> SPIF                 #
    ##################################################

    filename_mode_es = args.filename_mode_es

    if filename_mode_es != "":
        o_filename += "_es"
        with open(filename_mode_es) as csvfile:
            csvreader = csv.reader(csvfile)


            # create empty lists to store the data
            ev_sent = []
            ev_count = []

            # iterate through each row in the CSV file
            for row in csvreader:
                # print(row)
                # store the first column as ev_sent
                if float(row[2]) > 0 and float(row[1])<=data_x_limit:
                    ev_sent.append(float(row[1])/divider)
                    ev_count.append(float(row[2])/divider)

        ax.scatter(ev_sent, ev_count, label=mode_labels["mode_es"], color=mode_colors["mode_es"], alpha=1.0, s=mk_sz)


    ##################################################
    #                  ENET --> ENET                 #
    ##################################################

    filename_mode_ee = args.filename_mode_ee

    if filename_mode_ee != "":
        o_filename += "_ee"
        with open(filename_mode_ee) as csvfile:
            csvreader = csv.reader(csvfile)


            # create empty lists to store the data
            ev_sent = []
            ev_count = []

            # iterate through each row in the CSV file
            for row in csvreader:
                # print(row)
                # store the first column as ev_sent
                if float(row[2]) > 0 and float(row[1])<=data_x_limit:
                    ev_sent.append(float(row[1])/divider)
                    ev_count.append(float(row[2])/divider)

        ax.scatter(ev_sent, ev_count, label=mode_labels["mode_ee"], color=mode_colors["mode_ee"], alpha=1.0, s=mk_sz)

    

    ##################################################
    #                  General Tweaks                #
    ##################################################

    ax.set_xlim([min_in, max_in])
    ax.set_ylim([min_in, max_in])
    if use_log_scale:

        ax.set_xlabel('Events streamed to SpiNNaker [ev/s]')
        ax.set_ylabel('Events received from SpiNNaker [ev/s]')
        plt.xscale('log')
        plt.yscale('log')
        plt.grid(True, which="both", ls="-")
    else:
        ax.set_xlabel('Events streamed to SpiNNaker [kev/s]')
        ax.set_ylabel('Events received from SpiNNaker [kev/s]')
        plt.grid(True)

    # show the legend    
    plt.legend(loc="upper left", handletextpad=-0.2)
    # plt.legend(handletextpad=-0.5)


    # display the plot
    o_filename += ".png"
    plt.savefig(o_filename, dpi=300, bbox_inches='tight')

    plt.clf()

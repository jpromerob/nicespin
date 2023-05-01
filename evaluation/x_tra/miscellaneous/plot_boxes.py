import csv
import matplotlib.pyplot as plt
import argparse
import pdb
import matplotlib.ticker as ticker

def parse_args():

    parser = argparse.ArgumentParser(description='Plotter')
    parser.add_argument('-fn', '--filename', type= str, help="File name", default="")

    return parser.parse_args()


se_colors = {"enet": "#D93644", 
                "spyf": "#009900", 
                "spif": "#1955AF"}

thresholds = [1,2,3,4,5,6]

if __name__ == '__main__':


    args = parse_args()


    # open the CSV file
    filename = args.filename

    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile)


        labels = []
        ratio_ev_sent = []
        ratio_ev_in = []
        ratio_ev_out = []    
        ratio_ev_in_dropped = []
        ratio_ev_out_dropped = []         
        for th in thresholds:
            labels.append(f'{th}')
            ratio_ev_sent.append([])
            ratio_ev_in.append([])
            ratio_ev_out.append([])
            ratio_ev_in_dropped.append([])
            ratio_ev_out_dropped.append([])

        # pdb.set_trace()


        # iterate through each row in the CSV file
        for row in csvreader:
            idx_th = 0
            for th in thresholds:
                if abs(int(row[0])-1e6*th) < 5e4*th:
                    if th == 8 :
                        print(f'{row[0]} ... {row[1]} ... {row[3]} ... ')
                    ratio_ev_sent[idx_th].append(100*int(row[0])/int(row[0]))
                    ratio_ev_in[idx_th].append(100*int(row[1])/int(row[0]))
                    ratio_ev_out[idx_th].append(100*int(row[3])/int(row[1]))
                    ratio_ev_in_dropped[idx_th].append(100*int(row[2])/int(row[0]))
                    ratio_ev_out_dropped[idx_th].append(100*int(row[4])/int(row[1]))
                idx_th += 1

        # pdb.set_trace()
        


    ###########################################################
    ##                Handled Events (Input)                 ##
    ###########################################################
    fig, ax = plt.subplots(figsize=(5,5))

    # ax.set_aspect('equal')

    b_plot = ax.boxplot(ratio_ev_in, positions=thresholds, showfliers=False)

    for i in range(len(thresholds)):
        b_plot['boxes'][i].set(color=se_colors["spif"])
        b_plot['medians'][i].set(color='black')

    # Add some labels and titles
    ax.set_xticklabels(labels)
    ax.set_xlabel('Events streamed to SPIF [Mev/s]')
    ax.set_ylabel('% of streamed events handled by SPIF')
    ax.set_ylim([89, 101])
    ax.grid(True)


    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))


    # show the legend
    plt.legend()

    # display the plot
    plt.savefig(f"{filename[:-4]}_boxes_in.png", dpi=300, bbox_inches='tight')

    plt.clf()


    ###########################################################
    ##                Handled Events (Output)                ##
    ###########################################################

    fig, ax = plt.subplots(figsize=(5,5))

    b_plot = ax.boxplot(ratio_ev_out, positions=thresholds, showfliers=False)

    for i in range(len(thresholds)):
        b_plot['boxes'][i].set(color=se_colors["spif"])
        b_plot['medians'][i].set(color='black')

    # Add some labels and titles
    ax.set_xticklabels(labels)
    ax.set_xlabel('Events streamed to SPIF [Mev/s]')
    ax.set_ylabel('% of streamed events handled by SPIF')
    ax.set_ylim([89, 101])
    ax.grid(True)


    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))


    # show the legend
    plt.legend()

    # display the plot
    plt.savefig(f"{filename[:-4]}_boxes_out.png", dpi=300, bbox_inches='tight')


    ###########################################################
    ##                Dropped Events (Input)                 ##
    ###########################################################
    
    fig, ax = plt.subplots(figsize=(5,5))

    # ax.set_aspect('equal')

    b_plot = ax.boxplot(ratio_ev_in_dropped, positions=thresholds, showfliers=False)

    for i in range(len(thresholds)):
        b_plot['boxes'][i].set(color=se_colors["spif"])
        b_plot['medians'][i].set(color='black')

    # res_enet = plt.boxplot(enet_summary, positions=[1], showfliers=False)
    # res_enet['boxes'][0].set(color=se_colors["enet"])
    # res_enet['medians'][0].set(color='black')

    # Add some labels and titles
    ax.set_xticklabels(labels)
    ax.set_xlabel('Events streamed to SPIF [Mev/s]')
    ax.set_ylabel('% of streamed events dropped by SPIF')
    ax.set_ylim([-1, 9])
    ax.grid(True)


    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))


    # show the legend
    # plt.legend()

    # display the plot
    plt.savefig(f"{filename[:-4]}_boxes_in_dropped.png", dpi=300, bbox_inches='tight')

    plt.clf()


    ###########################################################
    ##                Dropped Events (Output)                ##
    ###########################################################

    fig, ax = plt.subplots(figsize=(5,5))

    b_plot = ax.boxplot(ratio_ev_out_dropped, positions=thresholds, showfliers=False)

    for i in range(len(thresholds)):
        b_plot['boxes'][i].set(color=se_colors["spif"])
        b_plot['medians'][i].set(color='black')

    # Add some labels and titles
    ax.set_xticklabels(labels)
    ax.set_xlabel('Events streamed to SPIF [Mev/s]')
    ax.set_ylabel('% of streamed events dropped by SPIF')
    ax.set_ylim([-1, 11])
    ax.grid(True)


    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))


    # show the legend
    plt.legend()

    # display the plot
    plt.savefig(f"{filename[:-4]}_boxes_out_dropped.png", dpi=300, bbox_inches='tight')



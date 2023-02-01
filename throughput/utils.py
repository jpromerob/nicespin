import argparse
import datetime


spin_spif_map = {"1": "172.16.223.2", 
                 "37": "172.16.223.106", 
                 "43": "172.16.223.98",
                 "13": "172.16.223.10",
                 "121": "172.16.223.122",
                 "129": "172.16.223.130"}


# python3 /home/juan/nicespin/throughput/sim_throughput.py -x 40 -y 40 -n 4 -b 1 -w 80 -m es

def get_filename(args):
    
    current_datetime = datetime.datetime.now()

    if args.direct:
        print("Direct Input --> Output Connection")
        mode = args.mode + "d"
    else:
        print("Indirect Input --> Output Connection")
        mode = args.mode + "c" # c for 'convolution'

    filename = mode
    filename += "_x" + str(args.width)
    filename += "_y" + str(args.height)
    filename += "_w" + str(args.weight)
    filename += "_l" + str(args.length)
    filename += "_t" + str(args.tau_ref)
    filename += "_b" + str(args.board)
    filename += current_datetime.strftime("_%Y%m%d_%Hh%M") +".csv"
    print("\n\n\nSaving simulation results in " + filename + "\n\n\n")
    
    return filename

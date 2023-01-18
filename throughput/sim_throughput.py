import multiprocessing
import argparse
import sys, os, time
import pdb
import datetime



from stimulation import *
from computation import *
from visualization import *



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
        mode = args.mode + "d"
    else:
        mode = args.mode + "c" # c for 'convolution'

    filename = args.mode
    filename += "_x" + str(args.width)
    filename += "_y" + str(args.height)
    filename += "_w" + str(args.weight)
    filename += "_t" + str(args.tau_ref)
    filename += "_b" + str(args.board)
    filename += current_datetime.strftime("_%Y%m%d_%Hh%M") +".csv"
    print("\n\n\nSaving simulation results in " + filename + "\n\n\n")

    return filename

def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-b', '--board', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="1")
    parser.add_argument('-m', '--mode', type= str, help="Input/Output Mode | ss/se/es/ee where s: SPIF and e:ENET", default="ss")
    parser.add_argument('-n', '--bin', type=int, help="Time bin in [s] (for event counts)", default=4)
    parser.add_argument('-i', '--ip', type= str, help="SPIF's IP address", default="172.16.223.2")
    parser.add_argument('-p', '--port', type=int, help="SPIF's port", default=3333)
    parser.add_argument('-r', '--remote-receiver', action="store_true", help="Remote Receiver")
    parser.add_argument('-x', '--width', type=int, help="Image size (in px)", default=40)
    parser.add_argument('-y', '--height', type=int, help="Image size (in px)", default=40)
    parser.add_argument('-w', '--weight', type=int, help="Kernel Weights", default=80)
    parser.add_argument('-f', '--tau-ref', type=int, help="Tau Refractory in [us]", default=100)
    parser.add_argument('-d', '--direct', action="store_true", help="Direct connection Input-->Output")


    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    try:
        args.ip = spin_spif_map[args.board]
        rig_command = f"rig-power 172.16.223.{int(args.board)-1}"
        print(f"Currently waiting for '{rig_command}' to end")
        os.system(rig_command)
        time.sleep(5)
    except:
        print("Wrong SpiNN-5 to SPIF mapping")
        quit()


    filename = get_filename(args)
    
    manager = multiprocessing.Manager()
    end_of_sim = manager.Value('i', 0)
    input_q = multiprocessing.Queue() # events
    output_q = multiprocessing.Queue() # events


    stim = Stimulator(args, input_q, end_of_sim)
    spin = Computer(args, output_q, stim)
    disp = Display(args, input_q, output_q, end_of_sim, filename)

    with spin:
        with stim:
            with disp:
                spin.run_sim()
                end_of_sim.value = 1 # Let other processes know that simulation stopped
                spin.wrap_up()
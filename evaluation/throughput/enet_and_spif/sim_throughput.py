import multiprocessing
import sys, os, time
import pdb
import argparse
import datetime


from stimulation import *
from computation import *
from annotation import *

def get_filename(args):
    
    current_datetime = datetime.datetime.now()

    filename = "data/"
    filename +== args.mode
    filename += "_x" + str(args.width)
    filename += "_y" + str(args.height)
    filename += "_l" + str(args.length)
    filename += "_b" + str(args.board)
    filename += current_datetime.strftime("_%Y%m%d_%Hh%M") +".csv"
    print("\n\n\nSaving simulation results in " + filename + "\n\n\n")
    
    return filename


spin_spif_map = {"1": "172.16.223.2", 
                 "37": "172.16.223.106", 
                 "43": "172.16.223.98",
                 "13": "172.16.223.10",
                 "121": "172.16.223.122",
                 "129": "172.16.223.130"}

def parse_args():

    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-b', '--board', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="1")
    parser.add_argument('-p', '--port', type=int, help="SPIF's port", default=3333)
    
    parser.add_argument('-x', '--width', type=int, help="Image size (in px)", default=640)
    parser.add_argument('-y', '--height', type=int, help="Image size (in px)", default=480)
    parser.add_argument('-l', '--length', type=int, help="Unit size in px", default=0)
    parser.add_argument('-n', '--bin', type=int, help="Time bin in [s] (for event counts)", default=4)    
    parser.add_argument('-m', '--mode', type= str, help="Input/Output Mode | ss/se/es/ee where s: SPIF and e:ENET", default="ss")

    return parser.parse_args()

if __name__ == '__main__':


    args = parse_args()
    args.ip = spin_spif_map[str(args.board)]

    current_datetime = datetime.datetime.now()
    filename = get_filename(args)

    try:
        rig_command = f"rig-power 172.16.223.{int(args.board)-1}"
        print(f"Currently waiting for '{rig_command}' to end")
        os.system(rig_command)
        time.sleep(5)
    except:
        print("Wrong SpiNN-5 to SPIF mapping")
        quit()


    
    manager = multiprocessing.Manager()
    end_of_sim = manager.Value('i', 0)
    input_q = multiprocessing.Queue() # events
    output_q = multiprocessing.Queue() # events


    stim = Stimulator(args, input_q, end_of_sim)
    spin = Computer(args, output_q, stim)
    wrtr = Writer(args, input_q, output_q, end_of_sim, filename)


    with spin:
        with stim:
            with wrtr:
                spin.run_sim()
                end_of_sim.value = 1 # Let other processes know that simulation stopped
                spin.wrap_up()
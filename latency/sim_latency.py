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

def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-b', '--board', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="1")
    parser.add_argument('-i', '--ip', type= str, help="SPIF's IP address", default="172.16.223.2")
    parser.add_argument('-p', '--port', type=int, help="SPIF's port", default=3333)
    parser.add_argument('-r', '--remote-receiver', action="store_true", help="Remote Receiver")
    parser.add_argument('-s', '--simulate-spif', action="store_true", help="Simulate SPIF")
    parser.add_argument('-x', '--width', type=int, help="Image size (in px)", default=16)
    parser.add_argument('-y', '--height', type=int, help="Image size (in px)", default=16)
    parser.add_argument('-w', '--weight', type=int, help="Kernel Weights", default=70)
    parser.add_argument('-t', '--runtime', type=int, help="Run Time, in seconds", default=30)
    parser.add_argument('-e', '--timestep', type=int, help="SpiNNaker Timestep in [us]", default=1000)



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

    current_datetime = datetime.datetime.now()
    if not args.simulate_spif:
        mode = "spif"
    else:
        mode = "enet"

    # filename = mode + "_" + str(args.width) + "x" + str(args.height) + "_w" + str(args.weight) + "_" + current_datetime.strftime("%Y%m%d_%Hh%M") +".csv"
    filename = mode + "_latency.csv"
    os.system(f"rm {filename}")
    print("\n\n\nSaving simulation results in " + filename + "\n\n\n")
    
    manager = multiprocessing.Manager()
    end_of_sim = manager.Value('i', 0)
    input_q = multiprocessing.Queue() # events
    output_q = multiprocessing.Queue() # events


    stim = Stimulator(args, input_q, end_of_sim)
    spin = Computer(args, output_q, stim)
    disp = Display(args, input_q, output_q, end_of_sim, filename)

    with spin:
        disp.lut = spin.lut
        with stim:
            with disp:
                spin.run_sim()
                end_of_sim.value = 1 # Let other processes know that simulation stopped
                spin.wrap_up()
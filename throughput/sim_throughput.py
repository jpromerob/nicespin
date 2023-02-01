import multiprocessing
import sys, os, time
import pdb
import datetime


from utils import *
from stimulation import *
from streamulation import *
from computation import *
from visualization import *


def parse_args():


    parser = argparse.ArgumentParser(description='SpiNNaker-SPIF Simulation with Artificial Data')

    parser.add_argument('-b', '--board', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="1")
    parser.add_argument('-m', '--mode', type= str, help="Input/Output Mode | ss/se/es/ee where s: SPIF and e:ENET", default="ss")
    parser.add_argument('-n', '--bin', type=int, help="Time bin in [s] (for event counts)", default=4)
    parser.add_argument('-i', '--ip', type= str, help="SPIF's IP address", default="172.16.223.2")
    parser.add_argument('-p', '--port', type=int, help="SPIF's port", default=3333)
    parser.add_argument('-x', '--width', type=int, help="Image size (in px)", default=40)
    parser.add_argument('-y', '--height', type=int, help="Image size (in px)", default=40)
    parser.add_argument('-l', '--length', type=int, help="Unit size in px", default=40)
    parser.add_argument('-d', '--direct', action="store_true", help="Direct connection Input-->Output")
    parser.add_argument('-z', '--spin-waiter', type=int, help="Time waiting for SpiNNaker to be ready", default=30)
    
    parser.add_argument('-w', '--weight', type=int, help="Kernel Weights", default=80)
    parser.add_argument('-f', '--tau-ref', type=int, help="Tau Refractory in [us]", default=100)
    parser.add_argument('-s', '--stream', action="store_true", help="SPIF streaming")
    parser.add_argument('-g', '--do-mapping', action="store_true", help="Create Mapping Files")
    parser.add_argument('-r', '--remote-receiver', action="store_true", help="Remote Receiver")


    return parser.parse_args()

if __name__ == '__main__':


    args = parse_args()

    filename = get_filename(args)

    # Create mapping files 
    if args.stream:
        if args.do_mapping:
            print("Creating Mapping Files ... ")
            os.system(f"python3 ~/nicespin/throughput/mapping.py -x {args.width} -y {args.height} -l {args.length}")

    try:
        args.ip = spin_spif_map[args.board]
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


    if args.stream:
        stim = Streamulator(args, input_q, end_of_sim)
    else:
        stim = Stimulator(args, input_q, end_of_sim)
    spin = Computer(args, output_q, stim)
    disp = Display(args, input_q, output_q, end_of_sim, filename)

    with spin:
        with stim:
            with disp:
                spin.run_sim()
                end_of_sim.value = 1 # Let other processes know that simulation stopped
                spin.wrap_up()
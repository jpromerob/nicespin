import socket
import struct
import argparse

def parse_args():

    parser = argparse.ArgumentParser(description='Something')

    parser.add_argument('-s', '--socket', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="/tmp/trash_socket")    

    return parser.parse_args()
   

if __name__ == '__main__':


    args = parse_args()

    # connect to the Unix socket
    unix_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    unix_sock.connect(args.socket)

    # receive the bytes from the socket
    data = unix_sock.recv(4)  # assuming integer is 4 bytes

    # convert bytes to integer
    my_int = struct.unpack('i', data)[0]

    # close the socket
    unix_sock.close()

    # print the integer
    print(my_int)
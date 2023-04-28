import socket
import struct
import argparse


def parse_args():

    parser = argparse.ArgumentParser(description='Something')

    parser.add_argument('-i', '--integer', type= int, help="a random integer", default=0)    
    parser.add_argument('-s', '--socket', type= str, help="SPIF's SpiNN-5 IP x.x.x.?", default="/tmp/trash_socket")    

    return parser.parse_args()
   

if __name__ == '__main__':


    args = parse_args()

    # create a Unix socket
    unix_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    unix_sock.bind(args.socket)
    unix_sock.listen(1)
    conn, _ = unix_sock.accept()

    # send data
    data = struct.pack('i', args.integer)
    conn.sendall(data)

    # close the connection and socket
    conn.close()
    unix_sock.close()
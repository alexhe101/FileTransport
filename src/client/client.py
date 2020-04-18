import sys
from pathlib import Path
import os
import socket
import zlib
import hashlib


def main():
    path = sys.argv[1]
    addr = sys.argv[2]
    port = int(sys.argv[3])
    compress = len(sys.argv) == 5
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))
    print(f"connected to {addr}:{port}")
    for f in file_glob(path):
        send_file(sock, named_file(f[0], f[1], compress))
    sock.send(int(0).to_bytes(4, byteorder='big'))
    sock.close()
    print(f"connection closed")


def file_glob(path):
    path = Path(os.path.normpath((Path(path).absolute())))
    return [[path.name, path]] if path.is_file()\
        else [[str(item.relative_to(path.parent)), item]
              for item in path.rglob('*') if item.is_file()]


class named_file():
    def __init__(self, name, path, compress=False):
        self.name = name.replace(os.sep, '/')
        self.name_size = len(self.name.encode('utf-8'))
        self.data = path.read_bytes()
        self.data_size = len(self.data)
        self.md5 = hashlib.md5(self.data)
        self.compress = compress
        if self.compress:
            self.data = zlib.compress(self.data)


def recv_waitall(sock, length):
    data = bytes()
    while length > 0:
        frag = sock.recv(length)
        length -= len(frag)
        data = b''.join([data, frag])
    return data


def send_file(sock, path):
    print(
        f"sending info: {path.name}, {path.data_size}bytes{', zlib' if path.compress else ''}")
    sock.send(path.name_size.to_bytes(4, byteorder='big'))
    sock.send(path.name.encode('utf-8'))
    sock.send(path.md5.digest())
    sock.send(int(path.compress).to_bytes(1, byteorder='big'))
    shift = int.from_bytes(recv_waitall(sock, 8), byteorder='big')
    if (shift == 0xffffffffffffffff):
        print('remote exists, skipping')
        return
    print(f"sending data from {'start' if shift==0 else shift}")
    sock.send((path.data_size-shift).to_bytes(8, byteorder='big'))
    sock.send(path.data[shift:])
    print('file sent')


if __name__ == '__main__':
    main()

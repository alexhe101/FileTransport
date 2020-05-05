import socket
from hashlib import md5
from os import sep
from os.path import normpath
from pathlib import Path
from sys import argv
from time import time
from zlib import compress

from dsocket import dsend, wrecv


def main():
    elapsed = time()
    total = 0
    path = argv[1]
    addr = argv[2]
    port = int(argv[3])
    compress = len(argv) == 5
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))
    print(f"connected to {addr}:{port}")
    for f in file_glob(path):
        total += f[1].stat().st_size
        send_file(sock, named_file(f[0], f[1], compress))
    sock.send(int(0).to_bytes(4, byteorder='big'))
    sock.close()
    print("connection closed")
    elapsed = time() - elapsed
    print(f"total size: {total}Bytes,")
    print(f"elapsed time: {elapsed}s,")
    print(f"speed: {total/elapsed/1024}KB/s")


def file_glob(path):
    path = Path(normpath((Path(path).absolute())))
    return [[path.name, path]] if path.is_file()\
        else [[str(item.relative_to(path.parent)), item]
              for item in path.rglob('*') if item.is_file()]


class named_file():
    def __init__(self, name, path, compress=False):
        self.name = name.replace(sep, '/')
        self.name_size = len(self.name.encode('utf-8'))
        self.data = path.read_bytes()
        self.data_size = len(self.data)
        self.md5 = md5(self.data)
        self.compress = compress
        if self.compress:
            self.data = compress(self.data)


def send_file(sock, path):
    print(
        f"sending info: {path.name}, {path.data_size}bytes{', zlib' if path.compress else ''}")
    sock.send(path.name_size.to_bytes(4, byteorder='big'))
    sock.send(path.name.encode('utf-8'))
    sock.send(path.md5.digest())
    sock.send(int(path.compress).to_bytes(1, byteorder='big'))
    shift = int.from_bytes(wrecv(sock, 8), byteorder='big')
    if (shift == 0xffffffffffffffff):
        print('remote exists, skipping')
        return
    print(f"sending data from {'start' if shift==0 else shift}")
    sock.send((path.data_size-shift).to_bytes(8, byteorder='big'))
    dsend(sock, path.data, shift)


if __name__ == '__main__':
    main()

import socket
from hashlib import md5
from os import remove, sep
from pathlib import Path
from sys import argv
from time import time
from zlib import compress, compressobj

from common import dsend, fglob, fmd5, fsend, wrecv


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
    for f in fglob(path):
        send_file(sock, f[0], f[1], compress)
    sock.send(int(0).to_bytes(4, byteorder='big'))
    sock.close()
    print("connection closed")
    elapsed = time() - elapsed
    print(f"total size: {total}Bytes,")
    print(f"elapsed time: {elapsed}s,")
    print(f"speed: {total/elapsed/0x100000}MB/s")


def send_file(sock, name, path, compress):
    name = name.replace(sep, '/')
    name_size = len(name.encode('utf-8'))
    data = None
    try:
        data = path.read_bytes()
        lmd5 = md5(data).digest()
        if compress:
            data = compress(data)
        data_size = len(data)
    except MemoryError:
        lmd5 = fmd5(path)
        if compress:
            with open(path, 'rb') as f:
                raw = f.read()
                compressed = compressobj().compress(raw)
                with open(path+'.zlib', 'wb') as w:
                    w.write(compressed)
            path = path+'.zlib'
        data_size = Path(path).stat().st_size
    sock.send(name_size.to_bytes(4, byteorder='big'))
    sock.send(name.encode('utf-8'))
    sock.send(lmd5)
    sock.send(int(compress).to_bytes(1, byteorder='big'))
    shift = int.from_bytes(wrecv(sock, 8), byteorder='big')
    if shift == 0xffffffffffffffff:
        print('remote exists, skipping')
        return
    if shift > 0:
        print(f"continuing from {shift}")
    sock.send((data_size-shift).to_bytes(8, byteorder='big'))
    if data:
        dsend(sock, data, shift)
    else:
        fsend(sock, path, shift)
        if compress:
            remove(path)


if __name__ == '__main__':
    main()

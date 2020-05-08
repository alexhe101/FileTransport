import socket
from hashlib import md5
from os import remove, sep
from pathlib import Path
from sys import argv
from zlib import decompressobj

from common import fmd5, frecv, wrecv


def main():
    path = argv[1]
    addr = argv[2]
    port = int(argv[3])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen(1)
    print(f"listening at {addr}:{port}, save into {path}")
    while True:
        conn, remote = sock.accept()
        print(f"{remote} accepted")
        try:
            while recv_file(conn, path):
                pass
            conn.close()
            print('remote closed normally')
        except ConnectionResetError:
            print('remote connection reset')
    sock.close()


def recv_file(conn, path):
    name_size = int.from_bytes(wrecv(conn, 4), byteorder='big')
    if(name_size == 0):
        return False
    name = wrecv(conn, name_size).decode('utf-8').replace('/', sep)
    save = Path(path).joinpath(name)
    temp = Path(path).joinpath(name+'.download')
    check = Path(path).joinpath(name+'.md5')
    rmd5 = wrecv(conn, 16)
    compress = int.from_bytes(wrecv(conn, 1), byteorder='big')
    print(f"file: {name}{', zlib' if compress else ''}")
    mode = 'wb'
    shift = 0
    if check.exists() and rmd5 == check.read_bytes():
        mode = 'ab'
        shift = temp.stat().st_size
        print(f"resuming  previous download at {shift}Byte")
    if save.exists() and rmd5 == fmd5(save):
        shift = 0xffffffffffffffff
        print('already exists, skipping')
    conn.send(shift.to_bytes(8, byteorder='big'))
    if shift == 0xffffffffffffffff:
        return True
    check.parent.mkdir(parents=True, exist_ok=True)
    check.write_bytes(rmd5)
    data_size = int.from_bytes(wrecv(conn, 8), byteorder='big')
    with temp.open(mode) as out:
        frecv(conn, data_size, out)

    if compress:
        with temp.open('rb') as r:
            compressed = r.read()
            decompressed = decompressobj().decompress(compressed)
            with save.open('wb') as w:
                w.write(decompressed)
        remove(temp)
    else:
        temp.rename(save)
    remove(check)
    return True


if __name__ == '__main__':
    main()

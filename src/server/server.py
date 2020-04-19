import sys
import socket
from pathlib import Path
import hashlib
import zlib
import os


def main():
    path = sys.argv[1]
    addr = sys.argv[2]
    port = int(sys.argv[3])
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


def recv_waitall(sock, length):
    data = bytes()
    while length > 0:
        frag = sock.recv(length)
        length -= len(frag)
        data = b''.join([data, frag])
    return data


def recv_file(conn, path):
    name_size = int.from_bytes(recv_waitall(conn, 4), byteorder='big')
    if(name_size == 0):
        return False
    name = recv_waitall(conn, name_size).decode('utf-8').replace('/', os.sep)
    save = Path(path).joinpath(name)
    temp = Path(path).joinpath(name+'.download')
    check = Path(path).joinpath(name+'.md5')
    md5 = recv_waitall(conn, 16)
    compress = int.from_bytes(recv_waitall(conn, 1), byteorder='big')
    print(f"info: {name}{', zlib' if compress else ''}")
    mode = 'wb'
    shift = 0
    if check.exists() and md5 == check.read_bytes():
        mode = 'ab'
        shift = temp.stat().st_size
        print(f"resuming  previous download at {shift}")
    if save.exists() and md5 == hashlib.md5(save.read_bytes()).digest():
        shift = 0xffffffffffffffff
        print('already exists, skipping')
    conn.send(shift.to_bytes(8, byteorder='big'))
    if shift == 0xffffffffffffffff:
        return True
    check.parent.mkdir(parents=True, exist_ok=True)
    check.write_bytes(md5)
    data_size = int.from_bytes(recv_waitall(conn, 8), byteorder='big')
    print(f"{data_size}bytes remaining")
    with temp.open(mode) as out:
        while data_size > 1024:
            data = recv_waitall(conn, 1024)
            out.write(data)
            data_size -= 1024
        out.write(recv_waitall(conn, data_size))
    save.write_bytes(zlib.decompress(temp.read_bytes())
                     if compress else temp.read_bytes())
    os.remove(temp)
    os.remove(check)
    print('download saved')
    return True


if __name__ == '__main__':
    main()

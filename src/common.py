from hashlib import md5
from pathlib import Path
from os.path import normpath


def wrecv(sock, length):
    data = b''
    while length > 0:
        frag = sock.recv(length)
        length -= len(frag)
        data = b''.join([data, frag])
    return data


def frecv(sock, length, out, progress=True):
    block = 0x100000
    while length > block:
        out.write(wrecv(sock, block))
        length -= block
        if progress:
            print(f"progress: {(length/0x100000):.3f}MB remaining", end='\r')
    out.write(wrecv(sock, length))
    if progress:
        print('all received'+' ' * 80)


def dsend(sock, data,  shift, progress=True):
    block = 0x100000
    while shift+block < len(data):
        sock.send(data[shift:shift+block])
        shift += block
        if progress:
            print(f"progress: {(shift/0x100000):.3f}MB sent", end='\r')
    sock.send(data[shift:])
    if progress:
        print('all sent'+' ' * 80)


def fsend(sock, path, shift, progress=True):
    block = 0x10000
    size = Path(path).stat().st_size
    with open(path, 'rb') as f:
        f.seek(shift)
        while f.tell() + block < size:
            sock.send(f.read(block))
            if progress:
                print(f"progress: {(f.tell()/0x100000):.3f}MB sent", end='\r')
        sock.send(f.read(size-f.tell()))
    if progress:
        print('all sent'+' ' * 80)


def fmd5(path):
    lmd5 = md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(0x100000), b""):
            lmd5.update(chunk)
    return lmd5.digest()


def fglob(path):
    path = Path(normpath((Path(path).absolute())))
    return [[path.name, path]] if path.is_file()\
        else [[str(item.relative_to(path.parent)), item]
              for item in path.rglob('*') if item.is_file()]

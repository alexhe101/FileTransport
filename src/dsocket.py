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
            print(f"progress: {length}bytes remaining\r")
    out.write(wrecv(sock, length))
    if progress:
        print('all received')


def dsend(sock, data,  shift, progress=True):
    block = 0x100000
    while shift+block < len(data):
        sock.send(data[shift:shift+block])
        shift += block
        if progress:
            print(f"progress: {shift}bytes sent\r")
    sock.send(data[shift:])
    if progress:
        print('all sent')

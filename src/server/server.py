import sys  # using sys.argv
import socket  # using socket.socket()
from pathlib import Path  # using Path
import hashlib  # using hashlib.md5()
import zlib  # using zlib.decompress()
import os  # using os.remove()


def main():
    # 获取目录、地址、端口
    path = sys.argv[1]
    addr = sys.argv[2]
    port = int(sys.argv[3])
    # 接受连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen(1)
    print(f"server listening at {addr}:{port}, files will be saved to {path}")

    # 接收数据
    try:
        while True:
            conn, remote = sock.accept()
            print(f"accepting files from {remote}")
            while recv_file(conn, path):
                pass
            print(f"connection from {remote} fininshed")
            conn.close()
    except ConnectionResetError:
        print("remote closed")
    except KeyboardInterrupt:
        print('manual exiting')
    sock.close()


def recv_file(sock, path):
    name_size = sock.recv(4)
    if name_size:
        # 接收文件名长度
        name_size = int.from_bytes(name_size, byteorder='big')
        if(name_size == 0):
            return False
        # 接受文件名和文件摘要
        name = sock.recv(name_size).decode('utf-8')
        if "\\" in name:
            name = os.sep.join(name.split("\\"))
        elif "/" in name:
            name = os.sep.join(name.split("/"))
        md5 = sock.recv(16)
        print(f"file: {name},md5: {md5.hex()}")
        # 中间文件和最终文件
        save = Path(path).joinpath(name)
        temp = Path(path).joinpath(name+'.download')
        # 断点续传、跳过已有和更新
        mode = 'wb'
        if temp.exists():  # 断点续传
            print("incomplete download found, continuing preivous download")
            sock.send(temp.stat().st_size.to_bytes(10, byteorder='big'))
            mode = 'ab'
        elif save.exists():
            localmd5 = hashlib.md5()
            with open(save, 'rb') as local:
                buf = local.read(1024)
                while buf:
                    buf = local.read(1024)
                    localmd5.update(buf)
            if md5 == hashlib.md5(save.open('rb').read()).digest():  # 跳过已有
                sock.send(int(0xffffffffffffffff).to_bytes(
                    10, byteorder='big'))
                print("identical file exists, remote ignored")
                return True
            else:  # 更新文件
                print("different file found in local, updating from remote")
                sock.send(int(0).to_bytes(10, byteorder='big'))
        else:
            sock.send(int(0).to_bytes(10, byteorder='big'))
        Path(temp.parent).mkdir(parents=True, exist_ok=True)
        # 写入临时文件
        with temp.open(mode) as out:
            # 接受压缩标志和数据长度
            compress = bool(int.from_bytes(sock.recv(1), byteorder='big'))
            data_size = int.from_bytes(sock.recv(10), byteorder='big')
            print(f"downloading {data_size} Bytes, compress={compress}")
            # 创建、覆盖或追加文件
            while data_size > 1024:
                out.write(sock.recv(1024))
                data_size -= 1024
            out.write(sock.recv(data_size))
        # 解压缩并保存文件
        data = temp.open('rb').read()
        if compress:
            data = zlib.decompressobj().decompress(data)
        with open(save, 'wb') as out:
            out.write(data)
        os.remove(temp)
        print('file saved')
    return True


if __name__ == '__main__':
    main()

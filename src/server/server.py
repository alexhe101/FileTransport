import sys  # using sys.argv
import socket  # using socket.socket()
from pathlib import Path  # using Path
import hashlib  # using hashlib.md5()
import zlib  # using zlib.decompress()
import os  # using os.remove()


def main():
    try:
        # 获取目录、地址、端口
        path = sys.argv[1]
        addr = sys.argv[2]
        port = int(sys.argv[3])
        # 接受连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((addr, port))
        sock.listen(1)
        print(f"listening at {addr}:{port}")

        # 接收数据
        try:
            while True:
                conn, remote = sock.accept()
                print(f"{remote} accepted")
                while recv_file(conn, path):
                    pass
                print(f"{remote} fininshed")
                conn.close()
        except ConnectionResetError:
            print("connection reset")
    except KeyboardInterrupt:
        print('manual exit')
    sock.close()


def recv_file(conn, path):
    name_size = conn.recv(4)
    if name_size:
        # 接收文件名长度
        name_size = int.from_bytes(name_size, byteorder='big')
        if(name_size == 0):
            return False
        # 接受文件名和文件摘要
        name = conn.recv(name_size).decode('utf-8')
        if "\\" in name:
            name = os.sep.join(name.split("\\"))
        elif "/" in name:
            name = os.sep.join(name.split("/"))
        md5 = conn.recv(16)
        # 接受压缩标志
        compress = int.from_bytes(conn.recv(1), byteorder='big') == 1
        print(f"file: {name},md5: {md5.hex()}, compress:{compress}")
        # 中间文件和最终文件
        save = Path(path).joinpath(name)
        temp = Path(path).joinpath(name+'.download')
        # 断点续传、跳过已有和更新
        mode = 'wb'
        shift = 0
        if temp.exists():  # 断点续传
            print("continue previous download")
            shift = temp.stat().st_size
            mode = 'ab'
        elif save.exists():
            if md5 == hashlib.md5(save.read_bytes()).digest():  # 已有
                shift = 0xffffffffffffffff
                print("identical file exists, remote ignored")
            else:  # 更新
                print("different exists on local, updating from remote")
        # 反馈偏移
        conn.send(shift.to_bytes(8, byteorder='big'))
        # 跳过已有
        if shift == 0xffffffffffffffff:
            return True
        # 创建路径文件夹、写入临时文件
        Path(temp.parent).mkdir(parents=True, exist_ok=True)
        with temp.open(mode) as out:
            # 接收数据长度
            data_size = int.from_bytes(conn.recv(8), byteorder='big')
            print(f"downloading {data_size} Bytes")
            # 创建、覆盖或追加文件
            while data_size > 1024:
                out.write(conn.recv(1024))
                data_size -= 1024
            out.write(conn.recv(data_size))
        # 解压缩并保存文件
        save.write_bytes(zlib.decompress(temp.read_bytes())
                         if compress else temp.read_bytes())
        os.remove(temp)
        print('file received')
    return True


if __name__ == '__main__':
    main()

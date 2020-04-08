import socket
import sys
from pathlib import Path

# 接受方
# 使用示例：python3 server.py abcd/ 0.0.0.0 1234
# argv[1]: abcd/ 应该是保存到该文件夹下(类似C:\User\Alex\下载)
# argv[2]: 0.0.0.0 是本地监听的地址
# argv[3]: 1234 是监听端口
# Ctrl+C 退出程序


def recv_data(sock, save_location):
    buffer = sock.recv(4)  # 获取文件名大小
    if buffer:
        file_name_size = int.from_bytes(buffer, byteorder="big")  # 获取文件名大小
        relative_path = sock.recv(file_name_size) .decode('utf=8')  # 获取文件名
        file_size = int.from_bytes(sock.recv(10), byteorder="big")  # 获取文件大小

        print(f'file new name is {relative_path}, filesize is {file_size}')

        # 获得保存位置到文件夹的路径
        # 如果文件夹所在不存在则创建(类似mkdir -p)
        save_path = Path(save_location).joinpath(relative_path)
        Path(save_path.parent).mkdir(parents=True, exist_ok=True)

        print("begin receiving")
        fp = open(save_path, 'wb')
        recvd_size = 0
        while file_size-recvd_size >= 1024:
            data = sock.recv(1024)
            fp.write(data)
            recvd_size += len(data)
        data = sock.recv(file_size-recvd_size)
        fp.write(data)
        print(f"file saved to {save_path}")
        fp.close()


if __name__ == '__main__':
    save_location = sys.argv[1]
    listen_addr = sys.argv[2]
    listen_port = int(sys.argv[3])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((listen_addr, listen_port))
    s.listen(1)
    print('wait for connection......')
    sock, addr = s.accept()  # 获得接收数据使用的套接字
    print(f"accept new connection from {addr}")
    try:
        while True:
            recv_data(sock, save_location)
    except KeyboardInterrupt:
        print('quiting')

    s.close()

import socket
import sys
from pathlib import Path

# 发送方
# 使用示例：python3 client.py abcd 123.123.123.123 1234
# argv[1]: abcd 可以是任意文件或文件夹的相对或绝对路径
# argv[2]: 123.123.123.123 是发送目的地的地址
# argv[3]: 1234 是目的地端口

# f 为文件到提供的文件夹的相对目录，用于传输报头
# source 为提供的文件夹，用于读取文件


def transportFile(sock, f, source):
    absolute = Path(source).parent.joinpath(f)  # 本地可访问文件路径

    header = getHeader(f, absolute)  # 生成头部
    sock.send(header[0])  # 传输文件名大小
    sock.send(header[1])  # 传输文件名
    sock.send(header[2])  # 传输文件大小

    fp = open(absolute, 'rb')
    while True:                        # 连续传送文件
        data = fp.read(1024)
        if not data:
            break
        sock.send(data)
    print(f"already transport {absolute}")


def getHeader(__p, __s):
    file_name = str(__p).encode('utf-8')  # (路径)文件名
    file_name_size = len(file_name).to_bytes(
        4, byteorder="big")  # 文件名长度(4Byte),
    file_size = Path(__s).stat().st_size.to_bytes(
        10, byteorder="big")  # 文件大小(10Byte)
    return [file_name_size, file_name, file_size]


def getListOfFiles(__s):
    __p = Path(__s)
    if __p.is_file():
        return [__p.name]   # 如果是文件则直接返回单元素列表
    else:
        return [__f.parent.relative_to(__p.parent).joinpath(__f.name)  # 将文件名加上文件夹的相对路径
                for __f in __p.rglob('*')   # 选择所有文件和文件夹
                if __f.is_file()]   # 仅选择文件


if __name__ == '__main__':
    source = sys.argv[1]
    remoteAddr = sys.argv[2]
    remotePort = int(sys.argv[3])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 建立TCP连接
    s.connect((remoteAddr, remotePort))  # 发起连接

    relative_files = getListOfFiles(source)  # 获得所有需要发送的所有文件

    for f in relative_files:
        transportFile(s, f, source)

    s.close()

import socket
import sys
from pathlib import Path

# 发送方
# 使用示例：python3 client.py abcd 123.123.123.123 1234
# argv[1]: abcd 可以是任意文件或文件夹的相对或绝对路径
# argv[2]: 123.123.123.123 是发送目的地的地址
# argv[3]: 1234 是目的地端口


def transportFile(sock, filepath):
    header = getHeader(filepath)       # 生成头部
    sock.send(header.encode('utf-8'))  # 传输头部

    fp = open(filepath, 'rb')
    while True:                        # 连续传送文件
        data = fp.read(1024)
        if not data:
            break
        sock.send(data)
    print("already transport", filepath)


def getHeader(__p):
    header = __p + ',' + str(Path(__p).stat().st_size)  # 报头：(路径)文件名,大小
    header = header.ljust(100, ' ')  # 空白填充到100
    return header


def getListOfFiles(__s):
    __p = Path(__s)
    if __p.is_file():
        return [__p.name]   # 如果是文件则直接返回单元素列表
    else:
        return [__f.parent.relative_to(__p.parent).joinpath(__f.name)  # 将文件名加上文件夹的相对路径
                for __f in __p.rglob('*')   # 选择所有文件和文件夹
                if __f.is_file()]   # 仅选择文件


if __name__ == '__main__':
    filePath = sys.argv[1]
    remoteAddr = sys.argv[2]
    remotePort = int(sys.argv[3])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 建立TCP连接
    s.connect((remoteAddr, remotePort))  # 发起连接

    totalFile = getListOfFiles(filePath)  # 获得所有需要发送的所有文件

    for f in totalFile:
        transportFile(s, f)

    s.close()

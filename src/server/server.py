import socket
import sys
import os
from pathlib import Path
import hashlib
import  zipfile

# 接受方
# 使用示例：python3 server.py /root 0.0.0.0 1234
# argv[1]: abcd/ 应该是保存到该文件夹下(类似C:\User\Alex\下载)
# argv[2]: 0.0.0.0 是本地监听的地址
# argv[3]: 1234 是监听端口
# Ctrl+C 退出程序
#########与client段同一个方法

def unzip(srcFile,dstDir):
    fz = zipfile.ZipFile(srcFile, 'r')
    for f in fz.namelist():
        fz.extract(f, dstDir)

def GetFileMd5(filepath):
    # 获取文件的md5
    myhash = hashlib.md5()
    f = open(filepath, "rb")
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()
##########返回32位
def recv_data(sock, save_location,zipFlag):
    buffer = sock.recv(4)  # 获取文件名大小
    if buffer:
        file_name_size = int.from_bytes(buffer, byteorder="big")  # 获取文件名大小
        if file_name_size==0:#表示一次文件夹的传输结束
            return -1

        relative_path = sock.recv(file_name_size).decode('utf=8')  # 获取文件名
        file_size = int.from_bytes(sock.recv(10), byteorder="big")  # 获取文件大小
        file_md5=sock.recv(32).decode('utf-8')# 获取文件MD5码
        print(f'file new name is {relative_path}, filesize is {file_size}')

        zipbuffer = sock.recv(4)
        zipFileNameSize = int.from_bytes(zipbuffer, byteorder="big")
        zipFileName = sock.recv(zipFileNameSize).decode("utf-8")
        zipFileSize = int.from_bytes(sock.recv(10), byteorder="big")

        # 获得保存位置到文件夹的路径
        # 如果文件夹所在不存在则创建(类似mkdir -p)
        if "\\" in save_location:
            os.sep.join(save_location.split("\\"))
        elif "/" in save_location:
            os.sep.join(save_location.split("/"))

        save_path = Path(save_location).joinpath(relative_path)
        if zipFlag==0:
            save_path_download=Path(save_location).joinpath(relative_path+".download")#### 尚未传输完成的文件尾部都是.download
        else:
            save_path_download = Path(save_location).joinpath(zipFileName + ".download")
        Path(save_path.parent).mkdir(parents=True, exist_ok=True)
        if(os.path.exists(save_path)):###存在 return结束此次传输,发送回去的2也会使客户端结束传输
            if(os.path.getsize(save_path)==file_size and GetFileMd5(save_path)==file_md5):
                exist_flag="2"
                print("status:2. ",save_path,": File exists")
                sock.send(exist_flag.encode('utf-8'))
                return 
            else:###### 和发送的文件不一样,覆盖
               # print("old_md5 is:"+GetFileMd5(save_path)+" but new is: "+file_md5)
                os.remove(save_path)
                
        if(os.path.exists(save_path_download)):
            recvd_size_befor = Path(save_path_download).stat().st_size.to_bytes(10, byteorder="big")  # 文件大小(10Byte)
            exist_flag="1"
            print("status:1. ",save_path ,":Resume from break point.")
            sock.send(exist_flag.encode('utf-8'))
            sock.send(recvd_size_befor)
            fp = open(save_path_download, "ab")####使用追加命令
            recvd_size=int.from_bytes(recvd_size_befor, byteorder="big")
        else:
            exist_flag="0"
            sock.send(exist_flag.encode('utf-8'))
            if zipFlag==1:
                save_path = zipFileName
                file_size=zipFileSize
            print("status:0",save_path,": begin receiving")
            fp = open(save_path_download, 'wb')
            recvd_size = 0
        ##### 判断完毕,开始接收了!
        while file_size-recvd_size >= 1024:
            data = sock.recv(1024)
            fp.write(data)
            recvd_size += len(data)
        data = sock.recv(file_size-recvd_size)
        fp.write(data)
        fp.close()
        os.rename(save_path_download,save_path)
        if zipFlag==1:
            unzip(save_path,os.path.split(save_path)[0])
            os.remove(save_path)
        print(f"file saved to {save_path}")

        return 1
            



if __name__ == '__main__':
    save_location = sys.argv[1]
    listen_addr = sys.argv[2]
    listen_port = int(sys.argv[3])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((listen_addr, listen_port))
    s.listen(1)
    try:
        while True:
            print('wait for connection......')
            sock, addr = s.accept()  # 获得接收数据使用的套接字
            print(f"accept new connection from {addr}")
            zipFlag= sock.recv(1).decode("utf-8")
            while True:
                current = recv_data(sock, save_location,zipFlag)
                if current==-1:
                    sock.close()
                    break
    except KeyboardInterrupt:
        print('quiting')
    except ConnectionResetError:
        print("远程连接终止")
    s.close()


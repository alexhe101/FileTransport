import socket
import os
def dealFilePath(fileName,controlBit,baseName=""):
    if controlBit==0:
        return os.path.split(fileName)[1]
    if controlBit==1:
        index = fileName.find(baseName)
        return fileName[index:]                #例如C:\User\Alex\FileTransport\text.py basename=FileTranport  可得到FileTransport\text.py


def recv_data(sock,addr,controlBit,baseName=""):
    msglen = eval(sock.recv(100).decode('utf-8').strip(' '))  # 第一次先发送一个头部信息的长度
    buffer = sock.recv(msglen) #获取头部信息
    if buffer:
        file_head = (buffer.decode('utf-8')).split(',')
        filePath = dealFilePath(file_head[0],controlBit,baseName) #获取带路径的文件名，或是单纯的文件名
        if controlBit==1:
            base_path,Name = os.path.split(filePath)
            if not os.path.exists(base_path):
               os.makedirs(base_path)#创建层级目录
        fileName = filePath #文件名，根据controlbit不同就带有不同的路径

        file_size = eval(file_head[1])
        print('file new name is {0}, filesize is {1}'.format(fileName, file_size))
        recvd_size = 0
        fp = open(fileName, 'wb')
        print("begin receiving")
        while recvd_size != file_size:
            if file_size - recvd_size > 1024:
                data = sock.recv(1024)
                recvd_size += len(data)
                #print("current size" + str(recvd_size))
            else:
                data = sock.recv(file_size - recvd_size)
                recvd_size = file_size
                #print("current size" + str(recvd_size))
            if not data:
                break
            fp.write(data)
        fp.close()
    else:
        print("no file recv")
    return  recvd_size


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#防止不发送数据时tcp连接马上关闭，用于接受最后一部分数据
    s.bind(('0.0.0.0',9999))
    s.listen(1)
    print('wait for connection......')
    sock,addr = s.accept() # 获得接收数据使用的套接字
    print("accept new connection from {0}".format(addr))
    controlBit= eval(sock.recv(1).decode('utf-8'))
    if controlBit==0: #
        recv_data(sock,addr,controlBit)
        sock.close()
        print("connection from %s:%s closed" % addr)
    if controlBit==1:
        base_Name = sock.recv(100).decode('utf-8').strip(" ")
        total_size= 0
        current_size = 0
        total_size =eval(sock.recv(100).decode('utf-8').strip(" "))
        while current_size!=total_size:
            current_size+=recv_data(sock,addr,controlBit,base_Name)
    sock.close()
    s.close()





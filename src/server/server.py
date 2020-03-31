import socket
import struct
import threading


def recv_data(sock,addr):
    print("accept new connection from {0}".format(addr))
    msglen = eval(sock.recv(100).decode('utf-8').strip(' '))#第一次先发送一个头部信息的长度
    print(msglen)
    buffer = sock.recv(msglen)
    if buffer:
        file_head = (buffer.decode('utf-8')).split(',')
        print("file_head")
        print(file_head)
        file_name = file_head[0]
        file_size = eval(file_head[1])
        print('file new name is {0}, filesize is {1}'.format(file_name, file_size))
        recvd_size = 0
        fp = open('./'+file_name,'wb')
        print("begin receiving")
        while recvd_size!=file_size:
            if file_size-recvd_size>1024:
                data = sock.recv(1024)
                recvd_size+=len(data)
                print("current size"+str(recvd_size))
            else:
                data= sock.recv(file_size-recvd_size)
                recvd_size = file_size
                print("current size" + str(recvd_size))
            if not data:
                break
            fp.write(data)
        fp.close()
    else:
        print("no file recv")

    sock.close()
    print("connection from %s:%s closed" % addr)



if __name__ == '__main__':
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#防止不发送数据时tcp连接马上关闭，用于接受最后一部分数据
    s.bind(('0.0.0.0',9999))
    s.listen(5)
    print('wait for connection......')
    while True:
        sock,addr = s.accept()
        t = threading.Thread(target=recv_data,args=(sock,addr))
        t.start()
        break#测试时还没用到多线程，先break



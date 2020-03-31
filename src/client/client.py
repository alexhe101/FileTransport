import socket
import struct
import os
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #建立TCP连接

    s.connect(('127.0.0.1', 9999))
    #读取文件,生成文件头部信息
    filepath = r'testcase.txt'
    fp = open(filepath,'rb')
    base_name = os.path.basename(filepath)
    file_size = os.stat(filepath).st_size
    fhead = base_name+','+str(file_size)
    fhead = fhead.encode('utf-8')

    message_info_size = str(len(fhead))#头部信息的长度，设定为100
    while len(message_info_size)<100:
        message_info_size = message_info_size+" "
    s.send(message_info_size.encode('utf-8'))

    s.send(fhead)
    while True:
        data = fp.read(1024)
        if not data:
            print('file send over')
            break
        s.send(data)
    s.close()

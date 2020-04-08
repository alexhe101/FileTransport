import socket
import os
''' 增加选择传输文件OR文件夹的功能 '''
''' 传输文件用标志0，传输文件夹用标志1，附带上文件夹中各文件大小'''

totalSize = 0 #传输目录的时候所有文件大小之和

def transportFile(sock,filepath):

    fp = open(filepath, 'rb')
    fhead = buildHeadInfo(filepath)
    fhead_size = buildFheadSize(fhead)
    sock.send(fhead_size.encode('utf-8')) #传输头部大小
    sock.send(fhead.encode('utf-8')) #传输头部信息
    while True:
        data = fp.read(1024)
        if not data:
            break
        sock.send(data)
    print("already transport",filepath)

def buildHeadInfo(filepath):
    file_size = os.stat(filepath).st_size #发送的时候传绝对路径
    fhead = filepath + "," + str(file_size)
    return fhead
def buildFheadSize(fhead):
    message_info_size = str(len(fhead))
    if len(message_info_size)<100:
        message_info_size = message_info_size.ljust(100," ")
    return message_info_size




def transportDir(sock,totalFile):
    for filepath in totalFile:
        transportFile(sock,filepath)

def sendControlBit(sock,func):
    if func==1:
        sock.send("0".encode('utf-8'))
    if func==2:
        sock.send("1".encode('utf-8'))

def getAllFile(filepath,totalFile):
    tmp = os.listdir(filepath)
    global totalSize
    for f in tmp:
        f = os.path.join(filepath,f)
        if os.path.isfile(f):
            totalFile.append(f)
            totalSize = totalSize+os.path.getsize(f)
        else:
            getAllFile(f, totalFile)




if __name__ == '__main__':
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #建立TCP连接

    totalFile = [] #储存需要发送的所有文件
    s.connect(('127.0.0.1', 9999))
    #读取文件,生成文件头部信息
    while True:
        print("choose function:")
        print("input 1 for single file")
        print("input 2 for files in dir")

        function = eval(input())
        print("input file name or dir name:")
        filepath = input()
        sendControlBit(s,function) #发送控制bit位

        if function==1:
            transportFile(s,filepath)
            print("transport a file") #完成单个文件传输



        if function==2:
            getAllFile(filepath,totalFile)
            base_path = os.path.split(filepath)[1]
            if len(base_path)<100:
                base_path = base_path.ljust(100," ")
            s.send(base_path.encode('utf-8')) #发送根目录信息
            totalSize = str(totalSize)
            if len(totalSize)<100:
                totalSize = totalSize.ljust(100," ")
            s.send(totalSize.encode('utf-8'))

            transportDir(s,totalFile)



        print("input exit to quit,other key to continue")
        control = input()
        if control=='exit':
            break
    s.close()

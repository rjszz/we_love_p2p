import os
import socket
import time
import configparser
import random
import threading

class Server():

    def __init__(self):

        self.IP="0.0.0.0"
        self.PORT=8888
        self.log="server.log"

        self.working=True
        self.PeerMessage={}
    
    
    def addLog(self,Log):
        fp=open(self.log,'a')
        fp.write(str(Log))
        fp.close()
    pass

    def ListenPort(self):
        print("Start working")
        # 1. 创建套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	 #绑定
        s.bind(("0.0.0.0", self.PORT))
    	 #监听
        s.listen(10)
    	 #处理
        # c, addr = s.accept()
        # print('Connect client: ', addr)
        while  self.working:
            c, addr = s.accept()
            t1=threading.Thread(target=self.Server_thread,args=(c, addr))
            t1.start()
            
                
        
    def Server_thread(self,c, addr):
        print('Connect client: ', addr)
        msg = c.recv(1024)
        print(msg)

        #新节点加入
        if(msg.decode()=='JOIN'):
            c.sendall("OK".encode())
            Peer=c.recv(1024).decode()
            #ip,port=msg.split(':')
            # IP_PORT=msg.split(':')
            # ip=IP_PORT[0]
            # port=IP_PORT[1]
            c.sendall(str(self.PeerMessage).encode())
            self.SpeardPeer(Peer)
            self.PeerMessage[Peer]=1

            now=time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
            Log=now+"："+Peer+" join into the p2p Network Successful\r\n"
            self.addLog(Log)
            print(self.PeerMessage)


        elif(msg.decode()=='Log'):
            c.sendall("OK".encode())
            Log=c.recv(1024).decode()
            self.addLog(Log)


        pass


    def SpeardPeer(self,Peer):

        if(self.PeerMessage):
            RandomIp=random.sample(self.PeerMessage.keys(),1)
            print("RandomIp:",RandomIp)

        for peer in self.PeerMessage.keys():
            print("peer:",peer)
            ip,port=peer.split(':')
            #print(ip,port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port)))

            if(self.PeerMessage and peer!=RandomIp[0]):
                s.sendall("AddPeer".encode())
            else:
                s.sendall("AddPeerAndSpeard".encode())

            s.recv(1024)    #等待OK

            s.sendall(Peer.encode())    #发送节点信息

        

        pass


if __name__ == '__main__':
	myserver=Server()
	myserver.ListenPort()

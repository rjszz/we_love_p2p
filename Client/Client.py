import os
import socket
import time
import configparser
import random
import threading


class Client():
	"""docstring for Client"""
	def __init__(self):

		self.LocalPort=6666
		self.IP="0.0.0.0"
		self.PORT=8888
		self.server_IP="0.0.0.0"
		self.server_PORT=8888
		self.publicDir="p2p"
		self.verson=0
		self.LastMTime=0
		self.log="client.log"
		self.SpreadSeed=1

		self.working=True
		self.PeerMessage={}	#节点信息{ip:port}


	def addLog(self,Log):
		fp=open(self.log,'a')
		fp.write(str(Log))
		fp.close()
		pass

	def GetTime(self):
		return time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())

	def getChangeFile(self):
		#给出的时间就是   self.LastMTime
		#给出的目录就是 self.publicDir
		
		lists=[]
		MTimeTmp=self.LastMTime
		for root, dirs, files in os.walk(self.publicDir):
			for file in files:
            # 获取文件所属目录
            #print(root)
            # 获取文件路径
				absroot=os.path.join(root,file).replace(self.publicDir,'')
				rootime=os.stat(os.path.join(root,file)).st_mtime  #目录时间
				#print(rootime)
				if self.LastMTime < rootime:
					if MTimeTmp<rootime:
						MTimeTmp=rootime
					lists.append(absroot.replace("\\","/"))
		#return 一个列表
		
		config = configparser.ConfigParser()
		config.read('config.ini')
		config.set('common','LastMTime',str(MTimeTmp))
		self.LastMTime=MTimeTmp
		if(lists):
			self.verson=self.verson+1
			config.set('common','verson',str(self.verson))
		return lists
		pass

	#读取配置文件
	def read_ini(self):			
		config = configparser.ConfigParser()
		config.read('config.ini')

		self.LocalPort=int(config.get('self','localport'))
		self.IP=str(config.get('self','ip'))
		self.PORT=int(config.get('self','port'))
		self.server_IP=str(config.get('server','ip'))
		self.server_PORT=int(config.get('server','port'))
		self.publicDir=str(config.get('common','publicDir'))
		self.verson=int(config.get('common','verson'))
		self.LastMTime=float(config.get('common','LastMTime'))
		self.log=str(config.get('common','log'))
		self.SpreadSeed=int(config.get('common','SpreadSeed'))
		pass


	def start(self):

		#读取配置文件
		self.read_ini()

		#print(self.PORT,self.server_IP,self.server_PORT,self.publicDir,self.LastMTime,self.verson,self.log)
		#publicDir不存在，创建
		if(not os.path.exists(self.publicDir)):
			os.mkdir(self.publicDir)

		#log不存在，创建
		if(not os.path.exists(self.log)):
			fp=open(self.log,'w')
			fp.close()

		#开始监听
		t1=threading.Thread(target=self.ListenPort)
		t1.start()
		#self.ListenPort()

		#请求加入p2p网络
		self.JoinP2P()

		
		#self.ListenInput()
		#开辟线程接受输入
		t1=threading.Thread(target=self.ListenInput)
		t1.start()
		pass


	def ListenPort(self):
    	# 1. 创建套接字
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	 #绑定
		s.bind(("0.0.0.0", self.LocalPort))
    	 #监听
		s.listen(10)
    	 #处理
		while  self.working:
			c, addr = s.accept()
			t1=threading.Thread(target=self.Client_thread,args=(c, addr))
			t1.start()

		pass


	def ListenInput(self):
		while self.working:
			input_mesg=str(input("$"))
			if(input_mesg == 'Update'):
				t1=threading.Thread(target=self.AskForTransFile)
				t1.start()
				#self.AskForTransFile()
				pass


			#if(input_mesg == 'Delete'):

		

	def JoinP2P(self):
		# 1. 创建套接字
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	# 2. 连接
		s.connect((self.server_IP, self.server_PORT))

		sendmsg="JOIN"
		s.sendall(sendmsg.encode())

		revmsg = s.recv(1024)
		if(revmsg.decode() == 'OK'):
			s.sendall((self.IP+':'+str(self.PORT)).encode())

		#获取服务器发送过来的节点信息
		Peer=s.recv(1024)
		self.PeerMessage= eval(Peer)
		s.sendall("OK".encode())
		now=self.GetTime()
		Log=now+"： join into the p2p Network Successful\r\n"
		self.addLog(Log)
		#print(self.PeerMessage)

	pass

	def Client_thread(self,c, addr):
		msg = c.recv(1024)
		#print(msg)
		#要求传播文件
		if(msg.decode()=='AskForTransFile'):
			self.AskForTransFile(c)

			#接收文件
		elif(msg.decode()=='RecvFile'):
			self.RecvFile(c)

		#添加新节点
		elif(msg.decode()=='AddPeer'):
			c.sendall('OK'.encode())
			peer=c.recv(1024).decode()
			self.PeerMessage[peer]=1

			#添加新节点并且传播
		elif(msg.decode()=='AddPeerAndSpeard'):
			c.sendall('OK'.encode())
			peer=c.recv(1024).decode()
			self.PeerMessage[peer]=1
			ip,port=peer.split(':')
			lists=self.getChangeFile()
			self.TransFile(ip,port,lists)

		#请求删除文件
		elif(msg.decode()=='AskForDelFile'):
			self.AskForDelFile(c)

			#删除文件
		elif(msg.decode()=='DelFile'):
			self.DelFile(c)

		pass


	#要求传播文件
	def AskForTransFile(self):

		PeerMessageTmp={}
		#传播过程
		while  self.PeerMessage:
			RandomIp=random.sample(self.PeerMessage.keys(),1)

			#创建线程集合
			thread_list=[]
			File_list=self.getChangeFile()

			for IP_PORT in RandomIp:
				ip,port=IP_PORT.split(':')
				t1=threading.Thread(target=self.TransFile,args=(ip,port,File_list))
				thread_list.append(t1)
			#开始进程
			for t in thread_list:
				t.start()
			for t in thread_list:
				t.join()

			for IP in RandomIp:
				PeerMessageTmp[IP]=self.PeerMessage[IP]
				del self.PeerMessage[IP]

			pass

		self.PeerMessage.update(PeerMessageTmp)

		pass

	#接收文件
	def RecvFile(self,c):
		c.sendall("OK".encode())

		NewVerson=c.recv(1024)
		if(int(NewVerson)<=self.verson):
			c.sendall("NO".encode())
			c.close()
			return
		
		c.sendall("OK".encode())

		key = "@$@"
		while True:
			dos=c.recv(1024).decode()
			#print(dos)
			if dos!='end':
				c.send("ok".encode())
				with open(self.publicDir+dos,"ab") as f:
					while True:
						data = c.recv(1024)
						#print(data)
						if not data:
							break
						if data.decode('utf-8')[-3:]==key:
							f.write(data[:-3])
							c.sendall(b'ok')
							break
						f.write(data)
				f.close()
				#print("接收完毕")
			else:
				break
		c.close()
		self.verson=int(NewVerson)

		Log=self.GetTime()+'：'+"The publicDir has Update to verson "+str(self.verson)+'\r\n'
		self.addLog(Log)

		self.SendLogToServer(Log)
		pass

	#请求删除文件
	def AskForDelFile(self,c):
		s.sendall("OK".encode())
		DelFileName=s.recv(1024)
		print("是否同意删除："+DelFileName)
		confirm=input()

		pass

	#删除文件
	def DelFile(self,c):
		s.sendall("OK".encode())
		path=s.recv(1024)
		if os.path.isdir(path):
			os.rmdir(path)
		else:
			os.remove(path)
		pass

	pass

	def TransFile(self,ip,port,lists):

		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect((ip, int(port)))

		s.sendall("RecvFile".encode())

		s.recv(1024)	#接收ok回复

		s.sendall(str(self.verson).encode())	#发送版本信息

		recvmsg=s.recv(1024)	#接收ok回复

		#对方已更新
		if(recvmsg.decode()!='OK'):
			s.close()
			return

		for i in range(len(lists)):
			s.send(lists[i].encode())
			#print("目录已发送")
			dos = s.recv(1024)
			#print(dos)
			if dos==(b'ok'):
				#print("开始发送文件")
				with open(self.publicDir+lists[i], 'rb') as f:
					for data in f:
						#print(data)
						s.sendall(data)
				f.close()
				#print("文件结束")
			s.send("@$@".encode())
			#print(str.encode())
			#等待回应ok
			s.recv(1024)	
            # print(dos)

		s.send(b'end')
		#print("关闭连接")
		s.close()
	

	def SendLogToServer(self,message):
		# 1. 创建套接字
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	# 2. 连接
		s.connect((self.server_IP, self.server_PORT))

		sendmsg="Log"
		s.sendall(sendmsg.encode())

		s.recv(1024)

		message="\r\nFrom "+str(self.IP)+":"+str(self.PORT)+'\n'+message
		s.sendall(message.encode())

		s.close()

if __name__ == '__main__':
	myclient=Client()
	myclient.start()
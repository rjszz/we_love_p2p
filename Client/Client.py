import os
import socket
import time
import configparser

class Client():
	"""docstring for Client"""
	def __init__(self):
		self.IP="0.0.0.0"
		self.PORT=8888
		self.server_IP="0.0.0.0"
		self.server_PORT=8888
		self.publicDir="p2p"
		self.verson=0
		self.LastMTime=0
		self.log="client.log"
		self.working=True

	def addLog(self,Log):
		fp=open(self.log,'a')
		fp.write(str(Log))
		fp.close()
		pass

	def getChangeFile(self):
		#给出的时间就是   self.LastMTime
		#给出的目录就是 self.publicDir

		#return 一个列表
		pass

	#读取配置文件
	def read_ini(self):			
		config = configparser.ConfigParser()
		config.read('config.ini')

		self.PORT=int(config.get('self','port'))
		self.server_IP=str(config.get('server','ip'))
		self.server_PORT=int(config.get('server','port'))
		self.publicDir=str(config.get('common','publicDir'))
		self.verson=int(config.get('common','verson'))
		self.LastMTime=float(config.get('common','LastMTime'))
		self.log=str(config.get('common','log'))

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
		self.ListenPort()

		#请求加入p2p网络
		self.JoinP2P()

		#开辟线程接受输入
		self.ListenInput()

		pass


	def ListenPort(self):
    	# 1. 创建套接字
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	 #绑定
		s.bind((self.IP, self.PORT))
    	 #监听
		s.listen(10)
    	 #处理
		while  self.working:
			msg = c.recv(1024)

			#要求传播文件
			if(msg.decode()==''):

			#接收文件
			elif(msg.decode()==''):

			#请求删除文件
			elif(msg.decode()==''):

			#删除文件
			elif(msg.decode()==''):

			pass

		pass


	def ListenInput():
		
		pass

	def JoinP2P(self):
		# 1. 创建套接字
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	# 2. 连接
		s.connect((self.server_IP, self.server_PORT))

		sendmsg="JOIN"
		s.sendall(sendmsg.encode())
		revmsg = s.recv(1024)

    	#确认是否服务器回复ok
		now=time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
		if(revmsg.decode().strip() == 'OK'):
			Log=now+"： join into the p2p Network Successful\r\n"
			self.addLog(Log)
		else:
			Log=now+"： join into the p2p Network failed\r\n"
			self.addLog(Log)
		pass


	#要求传播文件
	def AskForTransFile(self,s):
		pass

	#接收文件
	def RecvFile(self,s):
		pass

	#请求删除文件
	def AskForDelFile(self,s):
		pass

	#删除文件
	def DelFile(self,s):
		pass

	pass


if __name__ == '__main__':
	myclient=Client()
	myclient.start()
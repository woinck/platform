# -*- coding: UTF-8 -*-

import cPickle,socket,threading,time,sio,basic,os

#from sclientui import UI_Run
#from sclientlogic import Logic_Run

def _SocketConnect(host,port,connName,list = 1):
	global gProcess,gProc
	result = []
	serv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	try:
		serv.bind((host,port))
	except:
		print 'port occupied, the program will exit...'
		time.sleep(3)
		exit(1)
		
	#设定AI连接最大时间
	if connName == 'AI':
		print 'waiting ai'
		serv.settimeout(sio.AI_CONNECT_TIMEOUT)
		print '\n',
	else:
		serv.settimeout(None)
	serv.listen(list)
	print 'waiting for %s connection...\n' %(connName),
	'''
	#每有一个socket进入等待连接的状态，进程标记+1
	if gProc.acquire():
		gProcess += 1
		gProc.notifyAll()
		gProc.release()
	'''	
	for i in range(list):
		#进行连接
		try:
			result.append(serv.accept())
		except socket.timeout:
			print connName,i,'connection failed'
			time.sleep(3)
			exit(1)
		
		#每有一个socket连接成功（两个AI算一个socket）则进程标记+1
		print '\n%s%d connected: %s\n' %(connName,i+1,result[-1][1]),
		if gProc.acquire():
			gProcess += 1
			gProc.notifyAll()
			gProc.release()
	
	#logic或ui返回
	if len(result) == 1:
		return result[0]
	else:
		return result

class Sui(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.name = 'Thread-UI'
		
	def run_AI(self,conn,AIPath):
		if AIPath == None:
			conn.send('|')
		else:
			os.system('cmd /c start %s' %(AIPath))
	
	def run(self):
		global gProcess,rProcess,mapInfo,heroType,aiInfo,gameMode
		global rbInfo,reInfo,rCommand
		global ai_thread,logic_thread,logc_run
		
		#定义回放列表用于生成回放文件，每个元素储存一个回合的信息
		replayInfo=[]
		
		#与UI连接
		connUI,address = _SocketConnect(sio.HOST,sio.UI_PORT,'UI')
		
		#发送游戏模式、地图和AI信息
		gameMode,gameMapPath,gameAIPath=sio._recvs(connUI)
		
		
		if gameMode <= sio.PLAYER_VS_PLAYER:
			if not sio.DEBUG_MODE:
				logic_run.start()
				time.sleep(0.1)
			logic_thread.start()
		
		#读取地图文件
		mapInfo=sio._ReadFile(gameMapPath)
			
		#运行AI线程及文件
		while gProc.acquire():
			if gProcess != sio.LOGIC_CONNECTED:
				gProc.wait()
			else:
				#运行AI连接线程
				ai_thread.start()
				#运行AI1
				self.run_AI(connUI,gameAIPath[0])
				gProc.release()
				break
			gProc.release()
		
		while gProc.acquire():
			if gProcess != sio.ONE_AI_CONNECTED:
				gProc.wait()
			else:
				#运行AI2
				self.run_AI(connUI,gameAIPath[1])
				gProc.release()
				break
			gProc.release()
		
		#所有连接建立后，将游戏进度前调
		while gProc.acquire():
			if gProcess != sio.CONNECTED:
				gProc.wait()
			else:
				gProcess = sio.MAP_SET
				gProc.notifyAll()
				gProc.release()
				break
			gProc.release()
		
		#AI返回heroType后将其传回界面
		while gProc.acquire():
			if gProcess != sio.HERO_TYPE_SET:
				gProc.wait()
			else:
				sio._sends(connUI,(mapInfo,aiInfo))
				gProcess = sio.ROUND
				gProc.notifyAll()
				gProc.release()
				break
			gProc.release()
		
		#初始化完毕，进入回合==============================================================
		flag = False
		#等待回合初始信息产生完毕
		while gProcess < sio.OVER:
			while rProc.acquire():
				if rProcess == sio.START:
					rProc.wait()
				else:
					#发送回合信息
					sio._sends(connUI,rbInfo)
					rProc.release()
					break
				rProc.release()
			
			#等待回合所有信息产生完毕
			while rProc.acquire():
				if rProcess != sio.REINFO_SET:
					rProc.wait()
				else:
					#发送回合信息
					sio._sends(connUI,(rCommand,reInfo))
					#回合信息存至回放列表中
					replayInfo.append([rbInfo,rCommand,reInfo])
					rProcess = sio.START
					rProc.notifyAll()
					#若游戏结束则跳出循环
					if reInfo.over != -1:
						flag = True
					rProc.release()
					break
				rProc.release()
			if flag:
				break
		
		#向UI发送胜利方
		while gProc.acquire():
			if gProcess != sio.WINNER_SET:
				gProc.wait()
			else:
				sio._sends(connUI,winner)
				gProc.notifyAll()
				gProc.release()
				break
			gProc.release()
		
		#存回放文件
		if sio.REPLAY_MODE:	
			#检验回放文件目录
			try:
				os.mkdir(os.getcwd() + '\\ReplayFiles')
			except:
				pass
			#写入回放
			sio._WriteFile(replayInfo,os.getcwd() + '\\ReplayFiles\\' + sio._ReplayFileName(aiInfo))
			
		connUI.close()
		
class Slogic(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.name = 'Thread-Logic'
	
	def run(self):
		global gProcess,rProcess,mapInfo,heroType,aiInfo,rbInfo,reInfo,rCommand,winner

		#connLogic,address = _SocketConnect(sio.HOST,sio.LOGIC_PORT,'Logic')
		
		connLogic = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			connLogic.connect((sio.HOST,sio.LOGIC_PORT))
			print 'Logic connected'
		except:
			print 'logic connection failed, the program will exit...'
			time.sleep(2)
			exit(1)
			
		if gProc.acquire():
			gProcess += 1
			gProc.notifyAll()
			gProc.release()
			
		#发送游戏初始信息
		while gProc.acquire():
			if gProcess < sio.HERO_TYPE_SET:
				gProc.wait()
			else:
				base = sio.construct_base(mapInfo,heroType)###########################
				sio._sends(connLogic,basic.Begin_Info(mapInfo,base,heroType))
				gProc.release()
				break
			gProc.release()	
		
		#等待其他线程初始化完毕
		while gProc.acquire():
			if gProcess != sio.ROUND:
				gProc.wait()
			else:
				gProc.release()
				break
			gProc.release()
		
		#初始化完毕，进入回合==============================================================	
		
		while gProcess != sio.OVER:
			
			#接收回合开始信息
			while rProc.acquire():
				if rProcess != sio.START:
					rProc.wait()
				else:
					rbInfo = sio._recvs(connLogic)
					rProcess = sio.RBINFO_SET
					rProc.notifyAll()
					rProc.release()
					break
				rProc.release()
				
			#将命令发送至AI
			while rProc.acquire():
				#print 'logic acquired',rProcess
				if rProcess != sio.RCOMMAND_SET:
					rProc.wait()
				else:
					sio._sends(connLogic,rCommand)
					reInfo = sio._recvs(connLogic)
					rProc.release()
					break
				rProc.release()
			
			#判断游戏是否结束，并调整游戏进度标记
			if reInfo.over != -1:
				gProc.acquire()
				gProcess = sio.OVER
				gProc.notifyAll()
				gProc.release()

			#调整回合进度标记
			while rProc.acquire():
				rProcess = sio.REINFO_SET
				rProc.notifyAll()
				rProc.release()
				break	
		winner = sio._recvs(connLogic)
		
		#接收胜利方信息
		gProc.acquire()
		gProcess = sio.WINNER_SET
		gProc.notifyAll()
		gProc.release()
		
		connLogic.close()

class Sai(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.name = 'Thread-AI'
	
	def run(self):
		global gProcess,rProcess,mapInfo,heroType,aiInfo,rbInfo,reInfo,rCommand,gameMode
		
		#与AI进行socket连接
		[(connAI1,address1),(connAI2,address2)] = _SocketConnect(sio.HOST,sio.AI_PORT,'AI',2)
		connAI=[connAI1,connAI2]
		
		#设置命令限时
		for i in connAI:
			i.settimeout(sio.AI_CMD_TIMEOUT)
		
		#向AI传输地图信息并接收AI的反馈
		while gProc.acquire():
			if gProcess != sio.MAP_SET:
				gProc.wait()
			else:
				for i in range(2):
					try:
						sio._sends(connAI[i],mapInfo)
						aiInfoTemp,heroTypeTemp = sio._recvs(connAI[i])
						aiInfo.append(aiInfoTemp)
						heroType.append(heroTypeTemp)
					except socket.timeout:
						print '未收到AI',i+1,'的信息，将采用默认值'
						aiInfo.append('Player'+str(i+1))
						heroType.append(6)
				
				#调节游戏进度标记
				gProcess = sio.HERO_TYPE_SET
				gProc.notifyAll()
				gProc.release()
				break
			gProc.release()

		#初始化完毕，进入回合==============================================================
		
		#游戏回合阶段
		while gProcess < sio.OVER:

			#将回合开始信息发送至AI，并接收AI的命令
			while rProc.acquire():
				if rProcess != sio.RBINFO_SET:
					rProc.wait()
				else:
					#清空接收区缓存（其中可能有因超时而没收到的上一回合的命令）
					connAI[rbInfo.id[0]].settimeout(0)
					try:
						connAI[rbInfo.id[0]].recv(1024)
					except:
						pass
					connAI[rbInfo.id[0]].settimeout(sio.AI_CMD_TIMEOUT)
					
					
					sio._sends(connAI[rbInfo.id[0]],rbInfo)
					try:
						rCommand = sio._recvs(connAI[rbInfo.id[0]])
					except socket.timeout:
						rCommand = basic.Command()
					rProcess = sio.RCOMMAND_SET
					rProc.notifyAll()
					rProc.release()
					break
				rProc.release()
			
			#调整回合进度标记
			while rProc.acquire():
				if rProcess == sio.RCOMMAND_SET:
					rProc.wait()
				else:
					rProc.release()
					break
				rProc.release()
		
		#向AI发送结束标志
		for i in range(2):
			connAI[i].send('|')
			connAI[i].close()

			
class Prog_Run(threading.Thread):
	def __init__(self,progPath):
		threading.Thread.__init__(self)
		self.progPath=progPath
					
	def run(self):
		os.system('cmd /c start %s' %(self.progPath))


global mapInfo,heroType,aiInfo,rbInfo,reInfo,rCommand,winner,gameMode

aiInfo=[]
heroType=[]
reInfo=None

#设置进度标记
gProcess = sio.START
rProcess = sio.START
gProc=threading.Condition()
rProc=threading.Condition()

#运行线程		
ui_thread = Sui()
ai_thread = Sai()
ui_run = Prog_Run(os.getcwd() + sio.UI_FILE_NAME)
logic_run = Prog_Run(os.getcwd() + sio.LOGIC_FILE_NAME)
logic_thread = Slogic()

ui_thread.start()
if not sio.DEBUG_MODE:
	ui_run.start()

raw_input('')

# -*- coding: utf-8 -*-

import socket,threading,cPickle,sio,time,basic,os,field
#from sclientui import UI_Run
#from sclientlogic import Logic_Run

global gameOver,gProcess,rProcess,mapInfo,heroType,aiInfo,rbInfo,reInfo,rCommand
gProcess = sio.START
rProcess = sio.START
gameOver = -1

#aiInfo='ai1'

def _SocketConnect(host,port,connName,list=1):
	global gProcess,gProc
	serv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	try:
		serv.bind((host,port))
	except:
		print 'port occupied, the program will exit...'
		time.sleep(3)
		exit(1)
	serv.listen(list)
	print 'waiting for %s connection...\n' %(connName),
	while gProc.acquire():
		gProcess += 1
		gProc.notifyAll()
		gProc.release()
		break
	conn,address = serv.accept()
	print '\n%s connected: %s' %(connName,address),
	while gProc.acquire():
		gProcess += 1
		gProc.notifyAll()
		gProc.release()
		break
	return (conn,address)

class Sui(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.name='Thread-UI'
		
	def run(self):
		global gameOver,gProcess,rProcess,mapInfo,heroType,aiInfo,rbInfo,reInfo,rCommand
		connUI,address=_SocketConnect(sio.HOST,sio.UI_PORT,'UI')
		
		#发送地图和AI信息
		gameMode,gameMapPath,gameAIPath=sio._recvs(connUI)
		
		#read map
		mapInfo=field._ReadMap(gameMapPath)
		#run AI
		os.system('cmd /c start %s' %(gameAIPath))
		#give map to AI
		while gProc.acquire():
			if gProcess != sio.CONNECTED:
				gProc.wait()
			else:
				gProcess=sio.MAP_SET
				gProc.notifyAll()
				gProc.release()
				break
			gProc.release()
		
		while gProc.acquire():
			if gProcess != sio.HERO_TYPE_SET:
				gProc.wait()
			else:
				sio._sends(connUI,(mapInfo,aiInfo))
				gProcess=sio.ROUND
				gProc.notifyAll()
				gProc.release()
				break
			gProc.release()
		
		#初始化完毕，进入回合==============================================================
		
		#每回合发送回合信息，包括指令
		while gProcess != sio.OVER:
			#get rbInfo,rCommand reInfo from Logic
			while rProc.acquire():
				if rProcess != sio.REINFO_SET:
					rProc.wait()
				else:
					sio._sends(connUI,(rbInfo,rCommand,reInfo))
					rProcess = sio.START
					rProc.notifyAll()
					rProc.release()
					break
				rProc.release()
			
			sio._sends(connUI,(rbInfo,rCommand,reInfo))
			if reInfo.over != -1:
				break
		connUI.close()
		
class Slogic(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.name='Thread-Logic'
	
	def run(self):
		global gameOver,gProcess,rProcess,mapInfo,heroType,aiInfo,rbInfo,reInfo,rCommand

		replayInfo=[]
		
		connLogic,address=_SocketConnect(sio.HOST,sio.LOGIC_PORT,'Logic')
		
		#发送游戏初始信息
		while gProc.acquire():
			if gProcess < sio.HERO_TYPE_SET:
				gProc.wait()
			else:
				base=field.construct_base(mapInfo,heroType)
				sio._sends(connLogic,basic.Begin_Info(mapInfo,base,heroType))
				gProc.release()
				break
			gProc.release()	
			
		while gProc.acquire():
			if gProcess != sio.ROUND:
				gProc.wait()
			else:
				gProc.release()
				break
			gProc.release()
			
		#初始化完毕，进入回合==============================================================	
		
		while gProcess != sio.OVER:
			
			#give rbInfo to AI
			while rProc.acquire():
				if rProcess != sio.START:
					rProc.wait()
				else:
					rbInfo=sio._recvs(connLogic)
					rProcess = sio.RBINFO_SET
					rProc.notifyAll()
					rProc.release()
					break
				rProc.release()
				
			#get rcommand from AI
			while rProc.acquire():
				#print 'logic acquired',rProcess
				if rProcess != sio.RCOMMAND_SET:
					rProc.wait()
				else:
					sio._sends(connLogic,rCommand)
					reInfo=sio._recvs(connLogic)
					
					gameOver=reInfo.over
					if gameOver != -1:
						if gProc.acquire():
							gProcess=sio.OVER
							gProc.notifyAll()
							gProc.release()
					rProcess = sio.REINFO_SET
					rProc.notifyAll()
					rProc.release()
					break
				rProc.release()
			
			
			replayInfo.append([rbInfo,rCommand,reInfo])
		connLogic.close()

class Sai(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.name='Thread-AI'
	
	def run(self):
		global gameOver,gProcess,rProcess,mapInfo,heroType,aiInfo,rbInfo,reInfo,rCommand
		connAI,address=_SocketConnect(sio.HOST,sio.AI_PORT,'AI')
		
		#receive map from UI
		while gProc.acquire():
			if gProcess != sio.MAP_SET:
				gProc.wait()
			else:
				sio._sends(connAI,mapInfo)
				aiInfo,heroType = sio._recvs(connAI)
				gProcess = sio.HERO_TYPE_SET
				gProc.notifyAll()
				gProc.release()
				break
			gProc.release()
		
		#初始化完毕，进入回合==============================================================
		while gProcess != sio.OVER:
			#get rbInfo from Logic
			#give rCommand to Logic
			while rProc.acquire():
				#print 'ai acquired',rProcess
				if rProcess != sio.RBINFO_SET:
					rProc.wait()
				else:
					sio._sends(connAI,rbInfo)
					rCommand=sio._recvs(connAI)
					rProcess=sio.RCOMMAND_SET
					rProc.notifyAll()
					rProc.release()
					break
				rProc.release()
			while rProc.acquire():
				if rProcess == sio.RCOMMAND_SET:
					rProc.wait()
				else:
					rProc.release()
					break
			#print 'gProcess=',gProcess
		connAI.send('|')
		connAI.close()

		
gProc=threading.Condition()
rProc=threading.Condition()
		
ui_thread = Sui()
ui_thread.start()
logic_thread = Slogic()
logic_thread.start()
ai_thread = Sai()
ai_thread.start()


raw_input('')
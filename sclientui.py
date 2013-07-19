# -*- coding: utf-8 -*-
import socket,cPickle,sio,time,basic
print 'ui'
#def UI_Run():
	
conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
	conn.connect((sio.HOST,sio.UI_PORT))
except:
	print 'failed to connect, the program will exit...'
	time.sleep(2)
	exit(1)
	
gameMode='ai_vs_ai'
gameMapPath='C:\\Users\\woinck\\Documents\\GitHub\\platform\\SampleMap.Map'
gameAIPath=[]

gameAIPath.append('C:\\Users\\woinck\\Documents\\GitHub\\platform\\sclientai.py')
gameAIPath.append('C:\\Users\\woinck\\Documents\\GitHub\\platform\\sclientai.py')

sio._sends(conn,(gameMode,gameMapPath,gameAIPath))

#接收AI与地图信息
mapInfo,aiInfo=sio._recvs(conn)
print 'map recv'
#接收每回合信息
rbInfo,rCommand,reInfo=sio._recvs(conn)
while reInfo.over == -1:
	print 'rInfo recv'
	print 'over=',reInfo.over
	#展示
	rbInfo,rCommand,reInfo=sio._recvs(conn)

conn.close()
raw_input('ui end')


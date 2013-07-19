# -*- coding: UTF-8 -*-
import socket,cPickle,sio,time,basic,os
print 'ai'
#AI需要完成的函数有两个：GetHeroType() 与AI()
def GetHeroType(mapInfo):
	return (6,6)
	
def AI(rBeginInfo):
	return basic.Command((1,2),'attack',3)

	
aiInfo='Sample'

conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
	conn.connect((sio.HOST,sio.AI_PORT))
except:
	print 'failed to connect, the program will exit...'
	time.sleep(2)
	exit(1)

mapInfo=sio._recvs(conn)
sio._sends(conn,(aiInfo,GetHeroType(mapInfo)))

while True:
	rBeginInfo=sio._recvs(conn)
	print 'rbInfo got'
	if rBeginInfo != '|':
		sio._sends(conn,AI(rBeginInfo))
		print 'cmd sent'
	else:
		break

conn.close()
raw_input('ai end')
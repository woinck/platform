# -*- coding: UTF-8 -*-
import socket,cPickle,sio,time,basic
print 'logic'
serv=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
	serv.bind((sio.HOST,sio.LOGIC_PORT))
except:
	print 'port occupied, the program will exit...'
	time.sleep(3)
	exit(1)
serv.listen(1)
print 'waiting for platform connection...\n',
conn,address = serv.accept()
	
base=[]
beginInfo=sio._recvs(conn)
roundEndInfo=basic.Round_End_Info(beginInfo.base,(1,2,3),'route1',(1,0),(100,100),-1)
roundBeginInfo=basic.Round_Begin_Info((0,3),[(1,1),(2,2)],beginInfo.base)
i=0
print roundEndInfo.over

while roundEndInfo.over == -1:
	i+=1
	#发送每回合的开始信息
	sio._sends(conn,roundBeginInfo)

	#接收AI的命令
	roundCommand=sio._recvs(conn)
	print 'cmd recv'
	#do some calculation to get roundEndInfo here
	roundEndInfo=basic.Round_End_Info(beginInfo.base,(1,2,3),'route1',(1,0),(100,100),-1)
	
	if i==5:
		roundEndInfo.over=0
	#发送每回合结束时的信息
	print roundEndInfo.over
	sio._sends(conn,roundEndInfo)
	print 'reInfo sent'

#发送胜利方
sio._sends(conn,1)

conn.close()
raw_input('logic end')
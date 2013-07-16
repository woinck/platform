# -*- coding: UTF-8 -*-

import cPickle

HOST='127.0.0.1'
LOGIC_PORT=8801
UI_PORT=8802
AI_PORT=8803


START=0
WAITING=3
CONNECTED=6
MAP_SET=7
HERO_TYPE_SET=8
ROUND=9
OVER=10

RBINFO_SET=1
RCOMMAND_SET=2
REINFO_SET=3


#将对象以字符串形式通过指定连接发送
def _sends(conn,data):
	conn.send(cPickle.dumps(data))
	conn.send('|')

#接收字符串并将其转换为对象返回，空则返回'#'
def _recvs(conn):
	result = ''
	c = conn.recv(1)
	while c != '|':
		result=result + c
		c = conn.recv(1)
	if result == '':
		return '|'
	else:
		return cPickle.loads(result)
		
def _ReadAI(aiPath):
	return 'ai1'
	
def _ReadMap111111(mapFile):
	return 'map1'
	
def _WriteAI():
	pass
	
def _WriteMap():
	pass
	
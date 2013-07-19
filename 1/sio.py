# -*- coding: UTF-8 -*-

import cPickle,basic,time

HOST='127.0.0.1'
LOGIC_PORT=8801
UI_PORT=8802
AI_PORT=8803

#游戏/回合进程标记
START=0
U_L_WAITING=2
U_L_CONNECTED=4
AI_WAITING=5
ONE_AI_CONNECTED=6
CONNECTED=7
MAP_SET=8
HERO_TYPE_SET=9
ROUND=10
OVER=11

RBINFO_SET=1
RCOMMAND_SET=2
REINFO_SET=3

#一些常量
AI_CMD_TIMEOUT=1
AI_CONNECT_TIMEOUT=3

class MapInfo:
	def __init__(self,whole_map):
		self.mapInfo=whole_map
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

#从文件读取地图信息
def _ReadFile(filePath):
	with open(filePath,'r') as read:
		result=cPickle.load(read)
	return result

#将地图信息写入文件
def _WriteFile(fileInfo,filePath):
	with open(filePath,'w') as save:
		cPickle.dump(fileInfo,save)
	
def _ReplayFileName(aiInfo):
	result=''
	result += aiInfo[0]+'_vs_'+aiInfo[1]+'_'
	result += time.strftime('%Y%m%d-%H-%M-%S')
	result += '.rep'
	return result
	
def _DefaultCommand(rbInfo):
	return basic.Command((1,2),'attack',3)
	
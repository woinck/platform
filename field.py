# -*- coding: utf-8 -*-
import basic,sio


def construct_map(kind):
    if kind==basic.TURRET:
        return basic.Map_Turret(kind)
    elif kind==basic.TEMPLE:
        return basic.Map_Temple(kind)
    else:
        return basic.Map_Basic(kind)
#利用类型构造地图对象(除机关单独构造)
def get_position(string):
    x=(ord(string[0])-48)*10+(ord(string[1])-48)
    y=(ord(string[3])-48)*10+(ord(string[4])-48)
    return (x,y)

def _ReadMap(mapFile):
	map_file=open(mapFile,"r")
	whole_map=[];Gear=[];base=[[],[]]
	map_temple=[]#记录需每回合计数的神庙位置
	s=0;i=0
	while 1:
		string=map_file.readline()
		if string=="\n":
			break
		m=[];j=0
		for c in string[:-1]:
			kind=ord(c)-48
			m+=[construct_map(kind)]
			if kind==basic.TEMPLE:
				map_temple+=(i,j)
			if kind==basic.GEAR:
				s+=1
			j+=1
		whole_map+=[m]
		i+=1
	for i in range(1,s+1):
		string=map_file.readline()
		gear_position=get_position(string[:5])
		gear_control=[]
		while 1:
			if not string:
				break
			string=string[6:]
			if string=='\n':
				break
			gear_control+=[get_position(string[:5])]
		whole_map[gear_position[0]][gear_position[1]]=basic.Map_Gear(basic.GEAR,gear_control)
	#将读入的数字地图转化为类型地图        
	for i in [0,1]:
		string=map_file.readline()
		while string!='\n':
			c=string[0]
			position=get_position(string[2:7])
			if ord(c)-48==basic.WIZARD:
				base[i]+=[basic.Wizard(ord(c)-48,position)]
			else:
				base[i]+=[basic.Base_Unit(ord(c)-48,position)]
			string=string[8:]
	return sio.MapInfo(whole_map)
	#读入士兵    
	#文件操作:whole_map表示地形类型    
	#        base[0],base[1]列表表示士兵

def construct_base(map,hero_type):
	return [[1,2,3,4],[8,7,6,5]]
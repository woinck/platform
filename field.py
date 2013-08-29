# -*- coding: utf-8 -*-
import basic

def construct_map(kind):
	'''�������͹����ͼ����(�����ص�������)'''
	if kind == basic.TURRET:
		return basic.Map_Turret(kind)
	elif kind == basic.TEMPLE:
		return basic.Map_Temple(kind)
	else:
		return basic.Map_Basic(kind)
def get_position(string):
	x = (ord(string[0]) - 48) * 10 + (ord(string[1]) - 48)
	y = (ord(string[3]) - 48) * 10 + (ord(string[4]) - 48)
	return (x, y)
def print_position(point):
	string = ''
	num_0 = chr(point[0] / 10 + 48) + chr(point[0] % 10 + 48)
	num_1 = chr(point[1] / 10 + 48) + chr(point[1] % 10 + 48)
	string += num_0 + ',' + num_1
	return string

def get_map(route, whole_map, base):
	'''�ļ�����,�����ͼ
	   whole_map��ʾ��������	
	   base[0],base[1]�б��ʾʿ��
	   routeΪ��ͼ�洢·��'''
	map_file = open(route, "r")
	s = 0
	while 1:
		string = map_file.readline()
		if string == "\n":
			break
		m = []
		for c in string[:-1]:
			kind = ord(c) - 48
			m += [construct_map(kind)]
			if kind == basic.GEAR:
				s += 1
		whole_map += [m]
	for i in range(1, s+1):
		string = map_file.readline()
		gear_position = get_position(string[:5])
		gear_control_trap = []
		while 1:
			if not string:
				break
			string = string[6:]
			if string == '\n':
				break
			gear_control_trap += [get_position(string[:5])]
		string = map_file.readline()
		gear_control_barrier = []
		while 1:
			if not string:
				break
			string = string[6:]
			if string == '\n':
				break
			gear_control_barrier += [get_position(string[:5])]
		whole_map[gear_position[0]][gear_position[1]] = basic.Map_Gear(basic.GEAR, gear_control_trap, gear_control_barrier)
	#����������ֵ�ͼת��Ϊ���͵�ͼ		
	for i in [0,1]:
		string = map_file.readline()
		while string != '\n':
			c = string[0]
			position = get_position(string[2:7])
			base[i] += [basic.Base_Unit(ord(c) - 48, position)]
			string = string[8:]
	map_file.close()
	#����ʿ��
def print_map(route, whole_map, base):
	'''�ļ�����������ͼд���ļ�
	   whole_map��ʾ��������	
	   base[0],base[1]�б��ʾʿ��
	   routeΪ��ͼ�洢·��'''	
	map_file = open(route, 'w')
	map_gear = []
	for i in range(len(whole_map)):
		for j in range(len(whole_map[i])):
			map_file.write(chr(whole_map[i][j].kind + 48))
			if whole_map[i][j].kind == basic.GEAR:
				map_gear += [(i,j)]
		map_file.write('\n')
	map_file.write('\n')
	for i in map_gear:
		map_file.write(print_position((i[0],i[1])) + ':')
		for k in whole_map[i[0]][i[1]].trap:
			map_file.write(print_position(k) + ';')
		map_file.write('\n	 ;')
		for k in whole_map[i[0]][i[1]].barrier:
			map_file.write(print_position(k) + ';')
		map_file.write('\n')
	for i in range(2):
		for j in base[i]:
			map_file.write(chr(j.kind + 48) + ':' + print_position(j.position) + ';')
		map_file.write('\n')
#Ӧ��ʾ����
#whole_map = []; base = [[], []]
#get_map(u'C:\\Users\\woinck\\Documents\\GitHub\\platform\\Map.txt', whole_map, base)
#print_map(u'C:\\Users\\woinck\\Documents\\GitHub\\platform\\Map.txt', whole_map, base)

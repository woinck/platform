# -*- coding: UTF-8 -*-
import socket,cPickle,sio,time,basic,main
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
print 'platform connected: %s' %(str(address))

#
map_change = None
#


begin_Info = sio._recvs(conn)
base = begin_Info.base
whole_map = begin_Info.map
hero_type = begin_Info.hero_type
turn = 0; score = [0,0]; map_temple=[]; over = -1
base[0] = [basic.Hero(hero_type[0], base[0][0].position)] + base[0][1:]
base[1] = [basic.Hero(hero_type[1], base[1][0].position)] + base[1][1:]
base[0].sort(); base[1].sort()
for i in range(0,len(whole_map)):
    for j in range(0,len(whole_map[i])):
        if whole_map[i][j].kind == basic.TEMPLE:
            map_temple += [[(i, j), 0]]

while over == -1 and turn < basic.TURN_MAX:
    turn += 1
    main.perparation(whole_map, base, score, map_temple)
    for i in range(0, len(base[0])):
        for j in [0,1]:
            if base[j][i].life > 0:
                pass
				#is_die[j] = False
            move_range = main.available_spots(whole_map, base,(j,i))
            map_temple
            roundBeginInfo = basic.Round_Begin_Info((j,i), move_range, base,map_temple)
            #发送每回合的开始信息：
            sio._sends(conn, roundBeginInfo)
            #接收AI的命令：
            roundCommand = sio._recvs(conn)
            roundEndInfo = main.calculation(roundCommand, base, whole_map, move_range, map_change, map_temple,score,(j,i))
            #发送每回合结束时的信息：
            sio._sends(conn, roundEndInfo)
            over = roundEndInfo.over
            if over != -1:
                break
        if over != -1:
            break
        
winner = main.end_score(score, base, over)
sio._sends(conn, winner)
conn.close()
raw_input('logic end')

import basic

def available_spots(map_list, unit_list, source_num):
'''该函数用于计算当前地图下某单位的活动范围。
   传入参量map_list，为基本地图单元的二维数组
   储存了地图的全部信息。unit_list同样记录了所有
   单位的信息。source_num是一个元组，为(side_num, object_num)
'''
    #计算单位阻挡的位置
    u_block = [unit_list[i][j].position for i in range(2) for j in range(len(unit_list[i]))]

    d_spots = [] # 所有已经确定可到且松弛完毕的点
    a_spots = [] # 所有被松弛过，未确定可到的点
    a_weight = [] # a_spots的点中的权值

    # 将源点加入(备注：这里默认地图加了一圈)
    s_unit = unit_list[source_num[0]][source_num[1]] # 目标单位
    s_position = s_unit.position # 源点坐标
    a_spots = [s_position]
    a_weight = [0]
    while len(a_spots) != len(map_list) * len(map_list[0]):
        min_weight = min(a_weight) # 求a_weight中最小值
        if min_weight >= s_unit.move_range: # 到达极限
	    break
        s = a_weight.index(min_weight) # 取得其序号
        # 松弛操作
        p_modify = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for i in range(4):
            p = a_spots[s] + p_modify # 可以松弛的四个方向点
            if not (p in u_block or p in d_spots): # 松弛点的条件
                if p in a_spots: # 更新
                    lf = map_list[p[0]][p[1]].landform
                    p_id = a_spots.index(p)
                    if MOVE_COST[lf] + a_weight[s] < a_weight[p_id]:
                        a_weight[p_id] = MOVE_COST[lf] + a_weight[s]
                else:    #新加入
                    lf = map_list[p[0]][p[1]].landform
                    a_spots.append(p)
                    a_weight.append(a_weight[s] + MOVE_COST[lf])

        # 松弛结束后，将 s 从a序列删除， 将它加入到d序列中
        d.append(a_spots[s])
        a_spots.pop(s)
        a_weight.pop(s)
    return d_spots

def perparation(whole_map, base, score, map_temple):
    for i in map_temple:
        m=whole_map[i[0][0]][i[0][1]]
        if m.time >= basic.TEMPLE_UP_TIME:
            i[1]=m.up #有神符存在
        else:
            m.time += 1
        #神庙计时器+1
    for i in [0,1]:
        for j in range(0, len(base[i])):
            p = base[i][j].position
            if whole_map[p[0]][p[1]].kind == basic.TRAP:
                base[i][j].life -= basic.TRAP_COST
            #陷阱减生命
            elif whole_map[p[0]][p[1]].kind == basic.TURRET:
                whole_map[p[0]][p[1]].time += 1
                if whole_map[p[0]][p[1]].time == basic.TURRET_SCORE_TIME:
                    score[i] += whole_map[p[0]][p[1]].score
            #连续占有多回合炮塔积分
#每回合前准备阶段
def calaculation(command, base, whole_map, move_range, map_change, map_temple,score):
    move_position = command.move
    order = command.order
    w = command.target
    attack_1 = 0; attack_2 = 0
    if move_position in move_range and move_position != base[j][i].position:
        whole_map[base[j][i].position[j]][base[j][i].position[1]].leave(base[j][i])
        base[j][i].move(move_position)
        map_change += whole_map[move_position[0]][move_position[1]].effect(base[j][i], whole_map,[score[j]])
        for i in map_temple:
            if i[0] == move_position:
                i[1] = 0
    if order == 1 and w[0] == 1-j:
        if distance(base[j][i].position, base[1-j][w[1]].position) in base[j][i].attack_range:
            attack_1 = base[j][i].attack(base[1-j][w[1]])
        if base[1-j][w[1]].life > 0 and distance(base[j][i].position, base[1-j][w[1]].position) in base[1-j][w[1]].attacka_range:
            attack_2 = base[1-j][w[1]].attack(base[j][i])
        #攻击及反击
    elif order == 2 and w[0] == j:
        if distance(base[j][i].position, base[j][w[1]].position) == 1:
            base[j][i].skill(base[j][w[1]])
            #使用技能
    over = -1
    for i in [0,1]:
        r = True
        for j in base[i]:
            if j.life > 0:
                r = False
        if r:
            over = 1-i
            break
    return basic.Round_End_Info(base, map_change, route, (attack_1, attack_2), score, over)
#将传入指令计算后传出
def end_score(score, base, over):
    if over == -1:
        for i in [0,1]:
            for j in range(0, len(base[i])):
                if base[i][j].life > 0:
                if base[i][j].kind < 6:
                    score[i] += base[i][j].life * basic.BASE_SCORE
                else:
                    score[i] += base[i][j].life * basic.HERO_SCORE
        if score[1] != score[0]:
            over = (score[1] > score[0])
    return over
#结束后计算积分返回胜队，（-1表示平局）

import basic

def available_spots(map_list, unit_list, source_num):
'''�ú������ڼ��㵱ǰ��ͼ��ĳ��λ�Ļ��Χ��
   �������map_list��Ϊ������ͼ��Ԫ�Ķ�ά����
   �����˵�ͼ��ȫ����Ϣ��unit_listͬ����¼������
   ��λ����Ϣ��source_num��һ��Ԫ�飬Ϊ(side_num, object_num)
'''
    #���㵥λ�赲��λ��
    u_block = [unit_list[i][j].position for i in range(2) for j in range(len(unit_list[i]))]

    d_spots = [] # �����Ѿ�ȷ���ɵ����ɳ���ϵĵ�
    a_spots = [] # ���б��ɳڹ���δȷ���ɵ��ĵ�
    a_weight = [] # a_spots�ĵ��е�Ȩֵ

    # ��Դ�����(��ע������Ĭ�ϵ�ͼ����һȦ)
    s_unit = unit_list[source_num[0]][source_num[1]] # Ŀ�굥λ
    s_position = s_unit.position # Դ������
    a_spots = [s_position]
    a_weight = [0]
    while len(a_spots) != len(map_list) * len(map_list[0]):
        min_weight = min(a_weight) # ��a_weight����Сֵ
        if min_weight >= s_unit.move_range: # ���Ｋ��
	    break
        s = a_weight.index(min_weight) # ȡ�������
        # �ɳڲ���
        p_modify = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for i in range(4):
            p = a_spots[s] + p_modify # �����ɳڵ��ĸ������
            if not (p in u_block or p in d_spots): # �ɳڵ������
                if p in a_spots: # ����
                    lf = map_list[p[0]][p[1]].landform
                    p_id = a_spots.index(p)
                    if MOVE_COST[lf] + a_weight[s] < a_weight[p_id]:
                        a_weight[p_id] = MOVE_COST[lf] + a_weight[s]
                else:    #�¼���
                    lf = map_list[p[0]][p[1]].landform
                    a_spots.append(p)
                    a_weight.append(a_weight[s] + MOVE_COST[lf])

        # �ɳڽ����󣬽� s ��a����ɾ���� �������뵽d������
        d.append(a_spots[s])
        a_spots.pop(s)
        a_weight.pop(s)
    return d_spots

def perparation(whole_map, base, score, map_temple):
    for i in map_temple:
        m=whole_map[i[0][0]][i[0][1]]
        if m.time >= basic.TEMPLE_UP_TIME:
            i[1]=m.up #���������
        else:
            m.time += 1
        #�����ʱ��+1
    for i in [0,1]:
        for j in range(0, len(base[i])):
            p = base[i][j].position
            if whole_map[p[0]][p[1]].kind == basic.TRAP:
                base[i][j].life -= basic.TRAP_COST
            #���������
            elif whole_map[p[0]][p[1]].kind == basic.TURRET:
                whole_map[p[0]][p[1]].time += 1
                if whole_map[p[0]][p[1]].time == basic.TURRET_SCORE_TIME:
                    score[i] += whole_map[p[0]][p[1]].score
            #����ռ�ж�غ���������
#ÿ�غ�ǰ׼���׶�
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
        #����������
    elif order == 2 and w[0] == j:
        if distance(base[j][i].position, base[j][w[1]].position) == 1:
            base[j][i].skill(base[j][w[1]])
            #ʹ�ü���
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
#������ָ�����󴫳�
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
#�����������ַ���ʤ�ӣ���-1��ʾƽ�֣�

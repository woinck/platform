# -*- coding: utf-8 -*-
'''
	这是名为shortest的python模块，提供了用于解决“队式15”
	逻辑部分所需要的可以到达区域计算的函数。使用的是朴素的
	Dijkstra算法。
'''
import basic
#from field_shelve import read_from, write_to # For testing

def available_spots(map_list, unit_list, source_num, prev = None):
    '''该函数用于计算当前地图下某单位的活动范围。
    传入参量map_list，为基本地图单元的二维数组储存了地图的全部信息。
    unit_list是单位信息列表。
    source_num是一个元组，为(side_num, object_num)。
    形参prev的用法见README。
    返回一个列表，包含所有可到达的点，顺序是由近及远。'''
    #计算单位阻挡的位置
    u_block = [unit_list[i][j].position \
               for i in range(2) for j in range(len(unit_list[i]))]        
    d_spots = [] # 所有已经确定可到且松弛完毕的点
    s_unit = unit_list[source_num[0]][source_num[1]] # 目标单位
    s_position = s_unit.position # 源点坐标
    a_spots = [s_position] # 所有被松弛过，未确定可到的点
    a_weight = [0]         # 点中的权值
    row = len(map_list)
    column = len(map_list[0])
    prev_a = [0]
    d_index = -1 # 新增可达点在d_spots中的序号，用于计算prev
    while True:
        if a_weight == []:
            break
        min_weight = min(a_weight) # 求a_weight中最小值
        if min_weight > s_unit.move_range: # 到达极限
            break
        d_index += 1
        s = a_weight.index(min_weight) # 取得其序号
        # 松弛操作
        p_modify = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for i in range(4):
            # 可以松弛的四个方向点
            p = (p_modify[i][0] + a_spots[s][0], p_modify[i][1] + a_spots[s][1])
            if p[0] < 0 or p[1] < 0 or p[0] >= row or p[1] >= column:
                continue    
            if not (p in u_block or p in d_spots): # 松弛点的条件
                lf = map_list[p[0]][p[1]].kind # 松弛点的地形 

                move_cost = basic.FIELD_EFFECT[lf][0] # 该点的体力消耗
                if p in a_spots: # 更新
                    p_id = a_spots.index(p) # 松弛点在a_spots里的index
                    if move_cost + a_weight[s] < a_weight[p_id]:
                        a_weight[p_id] = move_cost + a_weight[s]
                        if a_weight[p_id] <= s_unit.move_range:
                            prev_a[p_id] = d_index
                else: 			#新加入
                    lf = map_list[p[0]][p[1]].kind
                    a_spots.append(p)
                    a_weight.append(a_weight[s] + move_cost)
                    if a_weight[s] + move_cost <= s_unit.move_range:
                        prev_a.append(d_index)
        # 松弛结束后，将 s 从a序列删除， 将它加入到d序列中
        d_spots.append(a_spots[s]) 
        if not prev == None:      
            prev.append(prev_a[s])
        a_spots.pop(s)
        a_weight.pop(s)
        prev_a.pop(s)
    return d_spots

def GetRoute(maps, units, idnum, end):
    route = []
    last = []
    #print "soulu"#for test
    try:
        #print idnum#for test
        print len(units[0]), len(units[1])#for test
        print "before avail"
        field = available_spots(maps, units, idnum, last)
        print "end avail"
        ind = field.index(end)
        start = units[idnum[0]][idnum[1]].position
        route.append(field[ind])
        while (start!=field[ind]):
            ind = last[ind]
            route.append(field[ind])
        route.reverse()
        return route
    except:
        print "excption" #raise error
    #possibility: 1. invalid pos 2. invalid idnum


if __name__=="__main__":
    import testdata
    print GetRoute(testdata.maps, testdata.units0, (0, 0), (1, 1))


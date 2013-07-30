﻿# -*- coding: UTF-8 -*-
import random
import time
#常量采用全字母大写，变量及函数全字母小写，类名首字母大写，单词用‘—‘隔开
random.seed(time.time())
TURN_MAX = 200
COORDINATE_X_MAX = 20
COORDINATE_Y_MAX = 20
SOLDIERS_NUMBER = 10

TURRET_RANGE = range(3,11)
TEMPLE_UP_TIME = 9
TURRET_SCORE_TIME = 5
TRAP_COST = 3

PLAIN = 0#平原
MOUNTAIN = 1#山地
FOREST = 2#森林
BARRIER = 3#屏障
TURRET = 4#炮塔
TRAP = 5#陷阱
TEMPLE = 6#神庙
GEAR = 7#机关
FIELD_EFFECT = {PLAIN:(1,0,0,0,0),
                MOUNTAIN:(2,0,0,0,1),
                FOREST:(2,0,0,1,0),
                BARRIER:(1,0,0,0,0),
                TURRET:(1,2,0,0,0),
                TRAP:(1,0,0,0,0),
                TEMPLE:(1,3,0,0,0),
                GEAR:(1,2,0,0,0)}
#(move_consumption, score, attack_up, speed_up, defence_up)
HERO_UP_LIMIT = 5
BASE_UP_LIMIT = 3
HERO_SCORE = 3
BASE_SCORE = 1

SABER = 0#剑士
LANCER = 1#枪兵
ARCHER = 2#弓兵
DRAGON_RIDER = 3#飞骑兵
WARRIOR = 4#战士
WIZARD = 5#法师
HERO_1 = 6
HERO_2 = 7
HERO_3 = 8
ABILITY = {SABER:(25,18,95,12,6,[1],5),
           LANCER:(25,17,90,13,7,[1],4),
           ARCHER:(25,17,90,12,6,[2],3),
           DRAGON_RIDER:(21,15,95,10,8,[1],2),
           WARRIOR:(30,20,85,15,5,[1],1),
           WIZARD:(21,10,90,12,6,[],0),
           HERO_1:(55,17,90,15,5,[1],6),
           HERO_2:(40,20,100,13,6,[1],6),
           HERO_3:(45,20,95,14,7,[1,2],6)}
#(LIFE, ATTACK, SPEED, DEFENCE, MOVE_RANGE, ATTACK_RANGE, MOVE_SPEED)
#WIZARD:不可攻击，ATTACK表示回复生命数
ATTACK_EFFECT = {SABER:{SABER:1, LANCER:0.5, ARCHER:1, DRAGON_RIDER:0.5, WARRIOR:1.5, WIZARD:1, HERO_1:1, HERO_2:1, HERO_3:1},
                 LANCER:{SABER:1.5, LANCER:1, ARCHER:1, DRAGON_RIDER:1, WARRIOR:0.5, WIZARD:1, HERO_1:1, HERO_2:1, HERO_3:1},
                 ARCHER:{SABER:1, LANCER:1, ARCHER:1, DRAGON_RIDER:2, WARRIOR:1, WIZARD:1, HERO_1:1, HERO_2:1, HERO_3:1},
                 DRAGON_RIDER:{SABER:1.5, LANCER:1, ARCHER:1, DRAGON_RIDER:1, WARRIOR:0.5, WIZARD:1, HERO_1:1, HERO_2:1, HERO_3:1},
                 WARRIOR:{SABER:0.5, LANCER:1.5, ARCHER:1, DRAGON_RIDER:1.5, WARRIOR:1, WIZARD:1, HERO_1:1, HERO_2:1, HERO_3:1},
                 HERO_1:{SABER:1, LANCER:1, ARCHER:1, DRAGON_RIDER:2, WARRIOR:1, WIZARD:1, HERO_1:1, HERO_2:1, HERO_3:1},
                 HERO_2:{SABER:1, LANCER:1, ARCHER:1, DRAGON_RIDER:2, WARRIOR:1, WIZARD:1, HERO_1:1, HERO_2:1, HERO_3:1},
                 HERO_3:{SABER:1, LANCER:1, ARCHER:1, DRAGON_RIDER:2, WARRIOR:1, WIZARD:1, HERO_1:1, HERO_2:1, HERO_3:1}}
#相克性
class Map_Basic:
    '''基本地形：平原、山地、森林、屏障、陷阱
    FIELD_EFFECT(move_consumption, score, attack_up, speed_up, defence_up)'''
    def __init__(self, kind):
        self.kind = kind
        self.score = FIELD_EFFECT[kind][1]
        self.move_consumption = FIELD_EFFECT[kind][0]
    def effect(self, w, m, score):
        '''地形效果'''
        w.attack += FIELD_EFFECT[self.kind][2]
        w.speed += FIELD_EFFECT[self.kind][3]
        w.defence += FIELD_EFFECT[self.kind][4]
        return []
    def leave(self, w):
        '''离开地形后能力恢复'''
        w.attack -= FIELD_EFFECT[self.kind][2]
        w.speed -= FIELD_EFFECT[self.kind][3]
        w.defence -= FIELD_EFFECT[self.kind][4]
class Map_Turret(Map_Basic):
    '''特殊地形：炮塔
    FIELD_EFFECT(move_consumption, score, attack_up, speed_up, defence_up)'''
    def __init__(self, kind):
        self.kind = kind
        self.score = FIELD_EFFECT[kind][1]
        self.move_consumption = FIELD_EFFECT[kind][0]
        self.time = 0
    def effect(self, w, m, score):
        if w.kind == ARCHER:
            w.attack_range = TURRET_RANGE
        return []
    def leave(self, w):
        if w.kind == ARCHER:
            w.attack_range = ABILITY[ARCHER][5]
        self.time = 0
class Map_Gear(Map_Basic):
    '''特殊地形：机关
    FIELD_EFFECT(move_consumption, score, attack_up, speed_up, defence_up)'''
    def __init__(self, kind, trap=[], barrier=[]):
        self.kind = kind
        self.score = FIELD_EFFECT[kind][1]
        self.move_consumption = FIELD_EFFECT[kind][0]
        self.trap = trap #陷阱触发,trap为坐标列表
        self.barrier = barrier #产生或消除屏障，barrier为坐标列表
        self.on = False #未开启状态
    def effect(self, w, m, score):
        if not self.on:
            for i in self.trap:
                m[i[0]][i[1]] = Map_Trap(TRAP)
            #陷阱出现
            for i in self.barrier:
                m[i[0]][i[1]] = Map_Basic(BARRIER + PLANE - m[i[0]][i[1]].kind)
            #屏障产生或消失
            self.on = True
            score[0] += self.score
            return [(TRAP, x) for x in self.trap] + [(m[x[0]][x[1]].kind, x) for x in self.barrier]
        else:
            return []
class Map_Temple(Map_Basic):
    '''特殊地形：神庙
    FIELD_EFFECT(move_consumption, score, attack_up, speed_up, defence_up)'''
    def __init__(self, kind):
        self.kind = kind
        self.score = FIELD_EFFECT[kind][1]
        self.move_consumption = FIELD_EFFECT[kind][0]
        self.time = 0 #神庙计数器 
        self.up = random.choice([1,2,3]) #下一个神符种类
    def effect(self, w, m, score):
        if self.time >= TEMPLE_UP_TIME and ((w.kind < 6 and w.up < BASE_UP_LIMIT) or (w.kind > 5 and w.up > HERO_UP_LIMIT)):
            w.up += 1
            if self.up == 1:
                w.attack += 1
            if self.up == 2:
                w.speed += 1
            if self.up == 3:
                w.defence += 1
            self.time = 0
            self.up = random.choice([1,2,3])
            score[0] += self.score
        return []
class Base_Unit:
    '''一般士兵
    (LIFE, ATTACK, SPEED, DEFENCE, MOVE_RANGE, ATTACK_RANGE, MOVE_SPEED)'''
    def __init__(self, kind, position = (0,0)):
        self.kind = kind
        self.up = 0 #士兵能力上升数
        self.position = position
        self.life = ABILITY[kind][0]
        self.attack = ABILITY[kind][1]
        self.speed = ABILITY[kind][2]
        self.defence = ABILITY[kind][3]
        self.move_range = ABILITY[kind][4]
        self.attack_range = ABILITY[kind][5]
        self.move_speed = ABILITY[kind][6]
    def move(self, x, y):
        '''移动至(x, y)'''
        self.position = (x, y)
    def attack(self, enemy):
        '''攻击 enemy'''    
        r = random.uniform(0,100)
        s = (r <= (self.speed*3 - enemy.speed*2))
        enemy.life -= (self.attack - enemy.defence) * s * ATTACK_EFFECT[self.kind][enemy.kind]
        return s
    def __lt__(self, orther):
        '''比较攻击顺序'''
        return self.move_speed > orther.move_speed
       
class Wizard(Base_Unit):
    '''法师
    (LIFE, ATTACK, SPEED, DEFENCE, MOVE_RANGE, ATTACK_RANGE, MOVE_SPEED)'''    
    def skill(self, other):
        '''对other使用回复技能'''
        other.life += self.attack
        if other.life > ABILITY[other.kind][0]:
            other.life = ABILITY[other.kind][0]
class Hero(Base_Unit):
    def skill(self, w):
        '''英雄技能'''
        pass
class Begin_Info:
    def __init__(self, whole_map, base, hero_type = [6,6]):
        self.map = whole_map #二维地图列表
        self.base = base #二维士兵列表，第一维表示队伍0/1
        self.hero_type = hero_type #二元数组表示两队英雄类型
class Round_Begin_Info:
    def __init__(self, move_unit, move_range, base, temple):
        self.id = move_unit #如(0,2)表示0队第三个士兵
        self.range = move_range #坐标列表，如[(0,0),(1,0)]
        self.base = base 
        self.temple = temple
#temple列表表示各神庙是否出现神符，如[[(1,1),0],[(2,3),2]]表示(1,1)处神庙无神符,(2,3)处神庙有2类神符        
class Command:
    def __init__(self,order = 0, move_position = 0, target_id = 0):
        self.move = move_position #坐标(x,y)
        self.order = order #0:待机，1:攻击，2:技能
        self.target = target_id #同Round_Begin_Info.move_unit
class Round_End_Info:
    def __init__(self, base, map_change, attack_effect, score, over = -1):
        self.base = base
        self.change = map_change #如[(TRAP,(1,1))]表示(1,1)处出现陷阱，详细见class Map_Gear
        self.score = score #二元数组，表示当前两队积分
        self.over = over #-1表示未结束，0表示0队胜，1表示1队胜
        self.effect = attack_effect #二元组表示攻击与反击方是否命中,1表示命中，0表示未命中，-1表示未攻击(超出攻击范围或已死亡),如(1,-1)表示攻击命中，目标未反击

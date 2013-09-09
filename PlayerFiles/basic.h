const int TURN_MAX = 200;
#define COORDINATE_X_MAX 20
#define COORDINATE_Y_MAX 20
#define SOLDIERS_NUMBER 10

//TURRET_RANGE = range(2,11)
const int TEMPLE_UP_TIME = 9;
const int TURRET_SCORE_TIME = 5;
const int TRAP_COST = 3;
#define GEAR_MAX_NUMBER 5
#define TEMPLE_MAX_NUMBER 5

const int PLAIN = 0;//ƽԭ
const int MOUNTAIN = 1;//ɽ��
const int FOREST = 2;//ɭ��
const int BARRIER = 3;//����
const int TURRET = 4;//����
const int TRAP = 5;//����
const int TEMPLE = 6;//����
const int GEAR = 7;//����
const int MIRROR = 8;//������

const int FIELD_EFFECT[][5] ={{1,0,0,0,0},
                              {2,0,0,0,1},
                              {2,0,0,1,0},
                              {1,0,0,0,0},
                              {1,2,0,0,0},
                              {1,0,0,0,0},
                              {1,3,0,0,0},
                              {1,2,0,0,0},
                              {1,0,0,0,0}};
//{move_consumption, score, attack_up, speed_up, defence_up}
const int HERO_UP_LIMIT = 5;
const int BASE_UP_LIMIT = 3;
const int HERO_SCORE = 3;
const int BASE_SCORE = 1;
const int HERO_1_REPAIR_COST = 5;
const int HERO_2_KILL_RATE = 10;
const int HERO_3_UP_TIME = 5;

const int SABER = 0;//��ʿ
const int LANCER = 1;//ǹ��
const int ARCHER = 2;//����
const int DRAGON_RIDER = 3;//�����
const int WARRIOR = 4;//սʿ
const int WIZARD = 5;//��ʦ
const int HERO_1 = 6;
const int HERO_2 = 7;
const int HERO_3 = 8;

const int ABILITY[][6] = {{25, 18, 95, 12, 6, 5},
                          {25, 17, 90, 13, 7, 4},
                          {25, 17, 90, 12, 6, 3},
                          {21, 15, 95, 10, 8, 2},
                          {30, 20, 85, 15, 5, 1},
                          {21, 10, 90, 12, 6, 0},
                          {55, 17, 90, 15, 5, 6},
                          {40, 20, 100, 13, 6, 6},
                          {45, 20, 95, 14, 7, 6}};
//{LIFE, ATTACK, SPEED, DEFENCE, MOVE_RANGE, MOVE_SPEED}
//WIZARD:���ɹ�����ATTACK��ʾ�ظ�������
const float ATTACK_EFFECT[][9] = {{1,   0.5, 1, 0.5, 1.5, 1, 1, 1, 1},
                                  {1.5, 1,   1, 1,   0.5, 1, 1, 1, 1},
                                  {1,   1,   1, 2,   1,   1, 1, 1, 1},
                                  {1.5, 1,   1, 1,   0.5, 1, 1, 1, 1},
                                  {0.5, 1.5, 1, 1.5, 1,   1, 1, 1, 1},
                                  {1,   1,   1, 1,   1,   1, 1, 1, 1},
                                  {1,   1,   1, 1,   1,   1, 1, 1, 1},
                                  {1,   1,   1, 1,   1,   1, 1, 1, 1},
                                  {1,   1,   1, 1,   1,   1, 1, 1, 1}};
typedef struct position
{int x, y;
}Position;

bool operator == (const Position& pos1, const Position& pos2)
{
	return (pos1.x==pos2.x && pos1.y==pos2.y);
}
bool operator != (const Position& pos1, const Position& pos2)
{
	return (!(pos1==pos2));
}

typedef struct soldier_basic
{int kind, life, attack, speed, defence, move_range, move_speed;
 int attack_range[2];//attack_range[1][0]��ʾ������Χ������
 int up;//���������޶�
 Position p;
}Soldier_Basic;

typedef struct begin_info
{int map[COORDINATE_X_MAX][COORDINATE_Y_MAX];//��ͼ��������
 Soldier_Basic soldier[SOLDIERS_NUMBER][2];//ʿ������ֲ�
 Position* trap[GEAR_MAX_NUMBER], barrier[GEAR_MAX_NUMBER];//���ؿ��Ƶ����弰�ϰ�λ��,����������
}Begin_Info;
//��ʼ����ѡ��
Begin_Info  initial;
//ȫ�ֱ���initial?�޸ĺ�ѡ�ֿ���ֱ��ʹ��
int hero_type[2];//ѡ�ִ�����Ӣ��ѡ����Ҫ������һ��

typedef struct round_begin_info
{int team_number;//����ţ�0��1��
 int move_id;//�ƶ���λ����ʾ�������е�move_id����
 Position* move_range;//��ʿ�����ƶ���Χ����
 int temple_state[TEMPLE_MAX_NUMBER];
 //��ʾ�������״̬��0���������1��2��3�������ͬ���ࣻ
}Round_Begin_Info;

typedef struct command
{Position destination;
 int order;//0:������1:������2:����
 int target_id;//Ŀ�굥λ
}Command;

Position* move_range(int team_number, int move_id)
{typedef struct spot
  {Position pos;
   int move_consume;}Spot;
 Soldier_Basic self = initial.soldier[move_id][team_number];
 int o = 0, s = 0, d = 0, i, j, b;
 Position end = {-1,-1};
 Position* result = (Position*)(malloc(self.move_range * self.move_range * sizeof(Position)));
 Spot* up_layer = (Spot*)(malloc(sizeof(Spot))), * down_layer;
 Position* other_block = (Position*)(malloc(SOLDIERS_NUMBER * sizeof(Position)));
 Position* self_block = (Position*)(malloc(SOLDIERS_NUMBER * sizeof(Position)));
 const Position direction[4] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
 int l = 1, a, i_x, i_y, t;
 short r;
 Position p;
 if(self.kind != DRAGON_RIDER)
  {for(j = 0; j < SOLDIERS_NUMBER; j++)
     {if(initial.soldier[j][1 - team_number].life > 0) {other_block[o] = initial.soldier[j][1 - team_number].p; o++;}
      if(initial.soldier[j][team_number].life > 0 && j != move_id) {self_block[s] = initial.soldier[j][team_number].p; s++;}
      }
   for(i = 0; i < COORDINATE_X_MAX; i++)
	for(j = 0; j < COORDINATE_Y_MAX; j++)
	  if(initial.map[i][j] == BARRIER) {other_block[o].x = i; other_block[o].y = j; o++;}
   }
 result[d] = self.p; d++;
 up_layer[0].pos = self.p; up_layer[0].move_consume = 1;
 for(i = 0; i < self.move_range; i++)
  {down_layer = (Spot*)(malloc((l * 4 + 1) * sizeof(Spot)));
   a = 0;
   for(j = 0; j < l; j++)
	   if(up_layer[j].move_consume >= FIELD_EFFECT[initial.map[up_layer[j].pos.x][up_layer[j].pos.y]][0])
		   for(t = 0; t < 4; t++)
		    {i_x = up_layer[j].pos.x + direction[t].x;
             i_y = up_layer[j].pos.y + direction[t].y;
			 if(0 <= i_x && i_x <= COORDINATE_X_MAX && 0 <= i_y && i_y<=COORDINATE_Y_MAX)
			   {r = 1;
			    p.x = i_x; p.y = i_y;
			    for(b = 0; b < o; b++)
					if(other_block[b].x == p.x && other_block[b].y == p.y) {r = 0;break;}
				for(b = 0; b < d; b++)
					if(p.x == result[b].x && p.y == result[b].y) {r = 0;break;}
				if(r)
				   {down_layer[a].pos = p;
				    down_layer[a].move_consume = 1;
					a++;
				    r = 1;
				    for(b = 0; b < s; s++)
				       if(self_block[b].x == p.x && self_block[b].y == p.y) r = 0;
				    if(r)
					  {result[d] = p;
					   d++;}
				    }
			    }
            }
	   else
	     {down_layer[a].pos = up_layer[j].pos;
          down_layer[a].move_consume = up_layer[j].move_consume + 1;
          a++;}
   l = a;
   free(up_layer);
   up_layer = down_layer;}
 free(up_layer); free(other_block); free(self_block);
 result[d] = end;
 return result;}

int* attack_range(int team_number, int move_id, Position* move_range)
{int* result = (int*)(malloc(SOLDIERS_NUMBER * sizeof(int)));
 Position end = {-1,-1}, pos;
 int j = 0, distance, i, k;
 Soldier_Basic target,self = initial.soldier[move_id][team_number];
 for(k = 0; k < SOLDIERS_NUMBER; k++)
  {target = initial.soldier[k][1 - team_number];
   for(i = 0; move_range[i].x != end.x; i++)
    {pos = move_range[i];
    distance = abs(target.p.x - pos.x) + abs(target.p.y - pos.y);
    if(distance >= self.attack_range[0] && distance <= self.attack_range[1] && target.life > 0)
     {result[j] = k; 
      j++;
	  break;}}
   }
 result[j] = -1; j++;
 result = (int*)(realloc(result, j * sizeof(int)));
 return result;}

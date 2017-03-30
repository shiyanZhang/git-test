#-*- coding: utf-8 -*-
from model import *
from Genetic_algo import *
from gurobipy.gurobipy import tuplelist
import csv

def Model_Test():
    n = 4
    Cd = 10
    Cr = 6
    P = 0.5
    budget =23
    K = 0


    d_monitor={ (0,0):1, (0,1): 1, (0,2): 0, (0,3): 0,
                (1,0):0, (1,1): 1, (1,2): 0, (1,3): 0,
                (2,0):0, (2,1): 0, (2,2): 1, (2,3): 1,
                (3,0):0, (3,1): 0, (3,2): 1, (3,3): 0}

    v_commu ={ (0,0):1, (0,1): 0, (0,2): 0, (0,3): 0,#无线通讯
               (1,0):0, (1,1): 1, (1,2): 1, (1,3): 0,
               (2,0):0, (2,1): 0, (2,2): 1, (2,3): 1,
               (3,0):0, (3,1): 1, (3,2): 0, (3,3): 1}

    edges = [(1,2)]  #无线通讯的矩阵中的边
    edges = tuplelist(edges)
    #print "edges:", edges
    #print "d_monitor: ", d_monitor
    #print "v_commu: ", v_commu
    Min_pollution(P,n,Cd,Cr,budget,d_monitor,v_commu,edges)
    My_algo(P,n,Cd,Cr,budget,d_monitor,v_commu,edges)

nodeNum = 60
len = 50
wid = 50
Cost_List = 1
CalcTime_List = 1
Budget = 40
K = 3
Cost_List = [0, 0, 0] #分别对应Gurobi_Cost = 0， TwoPhase_Cost = 0， SimpleMix_Cost = 0
CalcTime_List = [0, 0, 0]
Average_cost = [0, 0, 0]
Average_time = [0, 0, 0]
calcTimes = 10 #计算calcTimes次取平均

def SensingRange(nodeNum, len, wid, Cost_List, CalcTime_List, Budget, K ,pop_size, max_gen):
    Cd = 10
    Cr = 6
    P = 1
    length = len
    width = wid
    Nodes = generateNodes(length, width, nodeNum)   # 随机添加结点
    ####初始化d_monitor,即dij; 具体地通过设定时间阈值Time，随机生成i->j和j->i之间的传染时间，time_ij和time_ji,#####
    # 比较它们j与Time, 进而初始化d_monitor
    d_monitor = {}
    # Velocity = 4  # 米/秒    直接初始化时间，不用“距离/速度”来求得，因为那样既复杂也不不满足实际情况（i到j和j到i的传染时间应该不同）
    Time = 30     # 秒
    num = 0  #测试用
    for i in range(nodeNum):
        for j in range(nodeNum):
            if(i==j):
                d_monitor[i,j] = 1
            else:
                time_ij = random.uniform(1, 120)  #在threshold_Time取range(10,120,10),随机生成的时间time_ij则要在（1,120）之间随机选一个数
                if(time_ij<=Time):
                    d_monitor[i,j] = 1
                    num += 1
                else:
                    d_monitor[i,j] = 0
    # print  "d_monitor==1的数目(除<i,i>):", num
    print  "d_monitor:", d_monitor
    #####初始化水管网的边，即结点间的水管#####
    edges = []
    Comm_Dist = length / math.sqrt(nodeNum)#米，即Communication_Distance，表示sensor间通讯距离限制
    for i in range(nodeNum):
        for j in range(nodeNum):
            distance_ij = Nodes[i].calDistance(Nodes[j])
            if(distance_ij<=Comm_Dist and i != j):
                edges.append((i,j))
    # print "edges:", edges
    tupl_edges = tuplelist(edges)
    #####根据edges矩阵生成v_commu的值，v_commu[i,j]表示i与j的物理可达，即i一定可以通讯到j，只要它们之间的结点布置了sensor，因为这些结点都能在通讯范围内#####
    #例如，v_commu[0,3]=1代表0能通讯到3；注意v_commu[a,a]=0，除非存在b使（a,b）在edges中 v_commu[a,a]才=1,此时a->b->a通讯
    v_commu = {}
    # v_commu = {(0,0):1, (1,1):1, (2,2):1, (3,3):1, (0,1):0, (1,0):0, (0,2):1, (2,0):1, (0,3):0, (3,0):0, (1,2):0,
    #            (2,1):0, (1,3):0, (3,1):0, (2,3):0, (3,2):0}

    # for i,j in v_commu:
    #     if v_commu[i,j]==1:
    #         print "v_commu[i,j]", (i,j)
    allLink_edges = edges       #先得到任意两点间可否通讯的图，存在一个list中；然后再转换成v_commu字典形式
    for i in range(nodeNum):
        for j in range(nodeNum):
            if (i,j) in allLink_edges:      #即表示i到j有通讯
                for k in range(nodeNum):
                    if (k,j) in allLink_edges and k!=i:
                        allLink_edges.append((i,k))
    for i in range(nodeNum):                #判断一下对角线是否设为1
        for j in range(nodeNum):
            if (i,j) in allLink_edges:      #说明表示i到有向外的通讯，不是孤立点，则自己能回到自己
                allLink_edges.append((i,i))
    # print "allLink_edges", allLink_edges
    allLink_edges = list(set(allLink_edges))  #去除list中重复的
    # print "allLink_edges", allLink_edges

    for i in range(nodeNum):    #列表allLink_edges转换为字典v_commu表示
        for j in range(nodeNum):
            if (i,j) in allLink_edges:
                v_commu[i,j]=1
            else:
                v_commu[i,j]=0
    print "v_commu", v_commu

    currentTime_1 = getTime()
    #Gurobi_Cost = Min_pollution(P,nodeNum,Cd,Cr,Budget,d_monitor,v_commu,tupl_edges)
    Gurobi_Cost = 0
    currentTime_2 = getTime()
    #TwoPhase_Cost = My_algo(P,nodeNum,Cd,Cr,Budget,d_monitor,v_commu,edges)
    TwoPhase_Cost = 0
    currentTime_3 = getTime()
    Genetic_Cost = Genetic_Algo_V(P,nodeNum,Cd,Cr,Budget,d_monitor,v_commu,edges, pop_size, max_gen)
    currentTime_4 = getTime()

    Time_Gurobi_Cost = currentTime_2 - currentTime_1
    Time_MyAlgo_Cost = currentTime_3 - currentTime_2
    Time_Genetic_Cost = currentTime_4 - currentTime_3
    Cost_List[0] = Gurobi_Cost
    Cost_List[1] = TwoPhase_Cost
    Cost_List[2] = Genetic_Cost

    CalcTime_List[0] = Time_Gurobi_Cost
    CalcTime_List[1] = Time_MyAlgo_Cost
    CalcTime_List[2] = Time_Genetic_Cost


with open('genetic_maxgen_test.csv', 'wb') as csvfile:
        c = csv.writer(csvfile, dialect='excel')
        # c.writerow(['nodeNum'])
        # c.writerow([nodeNum])
        c.writerow(['max_gen', 'Gurobi_Cost','Myalgo_Cost','Genetic_Cost','Gurobi_min_calcu_time','Two_phase_algo_calcu_time','calcu_time'])
        ## SensingRange(nodeNum, square, threshold_Time, Cost_List, CalcTime_List)
        # for time in range((int)(threshold_Time/3), (int)(threshold_Time*4), 10):
        pop_size = 50
        max_gen = 100
        for max_gen in range(600, 1001, 100):  # (5, 45, 5)
            for i in range(calcTimes): #calcTimes次取平均值
                SensingRange(nodeNum, len, wid, Cost_List, CalcTime_List,Budget,K, pop_size, max_gen)
                Average_cost[0] += Cost_List[0]
                Average_cost[1] += Cost_List[1]
                Average_cost[2] += Cost_List[2]
                Average_time[0] += CalcTime_List[0]
                Average_time[1] += CalcTime_List[1]
                Average_time[2] += CalcTime_List[2]
            Average_cost[0] /= calcTimes
            Average_cost[1] /= calcTimes
            Average_cost[2] /= calcTimes
            Average_time[0] /= calcTimes
            Average_time[1] /= calcTimes
            Average_time[2] /= calcTimes
            print Average_cost[0], Average_cost[1], Average_cost[2]
            c.writerow([max_gen, int(Average_cost[0]), int(Average_cost[1]), int(Average_cost[2]), Average_time[0], Average_time[1], Average_time[2]])
            Average_cost = [0, 0 ,0]
            Average_time = [0, 0 ,0]




#Model_Test()

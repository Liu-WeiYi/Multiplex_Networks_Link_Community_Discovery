#!/usr/bin/env python
#coding:utf-8
"""
  Author:   uniqueliu JHY
  Purpose: 整个程序入口
  Created: 2016/7/10
"""

import matplotlib.pyplot as plt
import pickle
import networkx as nx

import practise # 实验单独放在一个py文件中

"""
1. 读入Noordin网络
"""
from noordindata import NoordinData
Noordin = NoordinData()
graphs = Noordin.GetNets()
graph_names = Noordin.GetNames()

#"""
#2. 通过模块度选择网络
#"""
#from pylouvain import LouvainCommunities
## 2.1 计算所有网络模块度
#for name in graph_names:
    #com,modularity = LouvainCommunities(graphs[name])
    #print('%s:\tModularity = %.4f'%(graphs[name].name,modularity))

"""
-------------------------------------------------------------------------------
        --- 实验1 --- 
随机选择6个网络组成一个网络，并判断模块度 
"""
#practise.practise_one(graph_names, graphs)
Choosed_Graphs_Name = ['4 Kinship','5 Training','6 Business & Finance','8 Friendship','9a Religious','9b Soulmates']
Choosed_Graphs = []
for name in Choosed_Graphs_Name:
    Choosed_Graphs.append(graphs[name])
"""
        --- 实验1 结论 --- 
  耗时：5min
  共有14张网络，随机选择6张进行组合，共有 3003 种组合方式
  其中，模块度最大为: 
        组合方式为: Choosed_Graphs_Name
-------------------------------------------------------------------------------
"""
"""
-------------------------------------------------------------------------------
        --- 实验2 --- 
随机选择i个网络组成一个网络，并判断模块度 其中 i∈[1,14]
"""
#practise.practise_two(graph_names, graphs)

"""
        --- 实验2 结论 --- 
  耗时：70min
  共有14张网络，随机选择i张进行组合
  其中，模块度从一张网络的0.88下降到14张网络的0.09；
       表明，网络越多，融合后生成的网络随机性越强！
-------------------------------------------------------------------------------
"""


"""
3. 生成 三种 对比网络 
    1. Binary_Net --- 上述网络生成的二值化网络
    2. Weighted_Net --- Binary_Net网络基础之上添加边的权重，且权重代表该条边在所有网络中出现的频次
    3. Neighbor_Net --- Binary_Net网络基础之上添加边的权重，且权重代表两个节点在所有网络中的相似性
"""
import ProjectionType_Multiplex_Community_Discovery as P_MCD
Binary_Net = P_MCD.ProjectionMethods(Choosed_Graphs).Projection_Binary()
#Weight_Net = P_MCD.ProjectionMethods(Choosed_Graphs).Projection_Weight()
#Neighbor_Net = P_MCD.ProjectionMethods(Choosed_Graphs).Projection_Neighbor()


"""
4. 对上述网络进行 单网络的连边检测
"""
import Link_Community_Discovery
Binary_Communities = Link_Community_Discovery.MultiplexNetworkLinkCommnityDiscovery([Binary_Net]).NodeCommunity
pickle.dump(Binary_Communities,open('Binary_Communities.pickle','wb'))
#Weight_Communities = Link_Community_Discovery.MultiplexNetworkLinkCommnityDiscovery([Weight_Net])
#Neighbor_Communities = Link_Community_Discovery.MultiplexNetworkLinkCommnityDiscovery([Neighbor_Net])

"""
5. 调用多网络连边检测
"""
Multiplex_Communities = Link_Community_Discovery.MultiplexNetworkLinkCommnityDiscovery(Choosed_Graphs).NodeCommunity
pickle.dump(Multiplex_Communities,open('Communities.pickle','wb'))

#"""
#比较划分的互信息量
#"""
#from CommunityValidation import *

#communities = [Binary_Communities,Weight_Communities,Neighbor_Communities,Multiplex_Communities]
#Result = Validation().CompairValidationHeatMap(['Binary','Weighted','Neighbor','Multiplex'],communities,'NMI',True)


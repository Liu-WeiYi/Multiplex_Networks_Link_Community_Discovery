#!/usr/bin/env python
#coding:utf-8
"""
  Author:  uniqueliu --<unique_liu@163.com>
  Purpose: 实现多种等评价社团划分好坏的度量方法:
           1. NMI --- 互信息量
           2. Ω Index --- Omega度量(多用于重叠社团)
           3. Modularity --- 模块度
  Created: 2016/7/7
"""
import numpy as np
import matplotlib.pyplot as plt

########################################################################
class Validation:
    """
    Purpose: 实现多种等评价社团划分好坏的度量方法:
        1. NMI --- 互信息量
        2. Ω Index --- Omega度量(多用于重叠社团)
        3. Modularity --- 模块度
    """

    #----------------------------------------------------------------------
    def __init__(self):
        pass
    
    #----------------------------------------------------------------------
    def __Has_Edge(self, node1,node2,graph):
        """判断是否存在边
        若存在，返回1;否则返回0"""
        if (node1,node2) in graph.edges() or (node2, node1) in graph.edges():
            return 1
        else:
            return 0
        
    
    #----------------------------------------------------------------------
    def __In_the_Same_Community_or_not(self,n1,n2,community):
        """判断两个节点是否在同一个社团中
        若在，则返回1；否则返回0"""
        for com in community:
            if n1 in com and n2 in com:
                return 1
        return 0
    
    #----------------------------------------------------------------------
    def __MonoplexGraph_ModularityCalculation(self,Community,graph):
        """计算 单网络 的模块度"""
        modularity = 0
        M = len(graph.edges()) # 网络的边数之和
        
        for nodeIdx1 in range(len(graph.nodes())):
            for nodeIdx2 in range(nodeIdx1+1,len(graph.nodes())):
                node1 = graph.nodes()[nodeIdx1]
                node2 = graph.nodes()[nodeIdx2]
                node1_degree = graph.degree(node1)
                node2_degree = graph.degree(node2)
                
                a_ij = self.__Has_Edge(node1,node2,graph)
                p_ij = (node1_degree*node2_degree)/(2*M)
                delta = self.__In_the_Same_Community_or_not(node1,node2,Community)
                
                modularity += (a_ij-p_ij)*delta
        
        modularity = modularity/(2*M)

        return modularity
        
            
        
    #----------------------------------------------------------------------
    def __MultiplexGraph_ModularityCalculation(self,Community,graphs):
        """计算 多网络 的模块度"""
        multi_modularity = 0
        # 取出所有点
        nodes = []
        for g in graphs:
            nodes.extend(g.nodes())
        nodes = list(set(nodes))
        # 初始化总强度
        miu = 0
        
        for nodeIdx1 in range(len(nodes)):
            for nodeIdx2 in range(nodeIdx1+1,len(nodes)):
                node1 = nodes[nodeIdx1]
                node2 = nodes[nodeIdx2]
                # 判断两节点是否属于同一个社团
                delta = self.__In_the_Same_Community_or_not(node1,node2,Community)
                
                for pIdx in range(len(graphs)):
                    for qIdx in range(pIdx,len(graphs)):
                        p = graphs[pIdx]
                        q = graphs[qIdx]
                        
                        if p == q:
                            W_p = len(p.edges())
                            if node1 in p.nodes():
                                S_i_p = p.degree(node1)
                            else:
                                S_i_p = 0
                            if node2 in q.nodes():
                                S_j_p = p.degree(node2)
                            else:
                                S_j_p = 0
                            
                            if (node1,node2) in p.edges() or (node2,node1) in p.edges():
                                omega_i_j_p = 1
                            else:
                                omega_i_j_p = 0
                            
                            multi_modularity += (omega_i_j_p - (S_i_p*S_j_p)/(2*W_p))*delta
                            miu += S_i_p+S_j_p
                            
                        if p != q:
                            if node1 in p.nodes() and node2 in q.nodes():
                                C_p_q = 1
                            else:
                                C_p_q = 0

                            multi_modularity += C_p_q*delta
                            if node1 in p.nodes():
                                miu += 1
                            if node2 in q.nodes():
                                miu += 1
                            
        multi_modularity = multi_modularity/miu
        
        return multi_modularity
    
    #----------------------------------------------------------------------
    @classmethod
    def DivideIndependentSet(cls, groups):
    
        independent_groups = []

        dependent_groups = [set(x) for x in groups]

        # 相关集合迭代
        while len(dependent_groups) is not 0:


            remain_groups = []

            # 处理每个集合独立部分
            for group in dependent_groups:

                diff_set = set()

                for group2 in dependent_groups:
                    if group is not group2:
                        diff_set.update(group2)

                independ_set = group.difference(diff_set)
                remain_set = group.difference(independ_set)

                if len(independ_set) is not 0:
                    independent_groups.append(independ_set)

                if len(remain_set) is not 0:
                    remain_groups.append(remain_set)



            next_dependent_groups = set()
            dependent_groups_len = len(remain_groups)

            for x in range(dependent_groups_len):
                for y in range(x+1, dependent_groups_len):

                    inters_set = remain_groups[x].intersection(remain_groups[y])

                    if len(inters_set) > 0:
                        next_dependent_groups.add(tuple(sorted(inters_set)))

            dependent_groups = [set(x) for x in next_dependent_groups]

        return [sorted(list(x)) for x in independent_groups]

    def NMI(self, Community1, Community2, isOverlapping=False):
        """两个社团的互信息量
        输入：Community1 --- 社团1；Community2 --- 社团2
        输出：NMI Index
        """
        _MI = 0

        if isOverlapping:
            Community1 = Validation.DivideIndependentSet(groups=Community1)
            Community2 = Validation.DivideIndependentSet(groups=Community2)

        # 获取各个社团的总规模
        # 主要用做 P(Ck) 的分母
        Community1_Number = 0
        Community2_Number = 0
        for C1 in Community1:
            Community1_Number += len(C1)
        for C2 in Community2:
            Community2_Number += len(C2)

        # 获取两个社团的总规模
        # 主要用做 P(Ck ∩ Cj) 的分母
        All_Nodes_Number = 0
        Community1_All_Nodes = []
        Community2_All_Nodes = []
        for C1 in Community1:
            Community1_All_Nodes.extend(C1)
        for C2 in Community2:
            Community2_All_Nodes.extend(C2)
        All_Nodes_Number = len(list(set(set(Community1_All_Nodes)|set(Community2_All_Nodes))))

        # 计算NMI
        for C1 in Community1:
            # 计算P(C1)
            P_C1 = len(C1)/Community1_Number
            for C2 in Community2:
                # 计算P(C2)
                P_C2 = len(C2)/Community2_Number
                # 计算P(C1 ∩ C2)
                P_C1_C2 = len(list(set(set(C1)&set(C2))))/All_Nodes_Number
                # 计算互信息量:
                inLog = P_C1_C2/(P_C1*P_C2)
                if P_C1_C2 == 0:
                    _MI += 0
                else:
                    import math
                    _MI += P_C1_C2*math.log2(inLog)

        return _MI

    #----------------------------------------------------------------------
    def Modularity(self, Community, graphs):
        """计算当前划分的模块度
        输入: Community --- 社团划分结果; graphs --- 网络集合的list, 
        其中: 
            len(graphs) == 1: 当网络集合中只存在一个网络时，表明计算 单网络 的模块度;
            len(graphs) >= 1: 当网络集合中存在不止一个网络时，表明计算 多网络 的模块度;
        输出: Modularity
        """
        # 初始化模块度
        Modularity = 0
        # graphs
        if type(graphs) == list:
            #  判断网络个数 --- 只有一个网络 Flag == False; 有多个网络 Flag == True
            MultiGraphFlag = True
            if len(graphs) == 1:
                MultiGraphFlag == False
                graph = graphs[0]
            elif len(graphs) > 1:
                MultiGraphFlag == True
            else:
                print('网络输入有误, 请检查。。。')
        else:
            graph = graphs
            MultiGraphFlag = False
            
        if MultiGraphFlag == False:
            Modularity = self.__MonoplexGraph_ModularityCalculation(Community, graph)
        elif MultiGraphFlag == True:
            Modularity = self.__MultiplexGraph_ModularityCalculation(Community, graphs)
        
        return Modularity
    
    #----------------------------------------------------------------------
    def CompairValidationHeatMap(self,CommunityNameList,CompairCommunityList,ValidationMethod = 'NMI', ShowOrNot = True):
        """展示社团发现结果的热图
        输入: 
        CommunityNameList --- 社团结果名称列表
        CompairCommunityList --- 需要进行比较的社团划分结果
        ValidationMethod --- 需要选择的评价指标, 默认为 NMI
        ShowOrNot --- 是否需要显示, 默认为 TRUE(显示)
        输出:
        ValidationMatrix --- 几种比较结果的矩阵
        """
        ValidationMatrix = []
        minValue = 0
        maxValue = 0
        # 计算 评价 矩阵
        for idx in range(len(CompairCommunityList)):
            currentLineResult = []
            for idx2 in range(len(CompairCommunityList)):
                if idx == idx2:
                    currentNMI = 1
                else:
                    currentNMI = Validation().NMI(CompairCommunityList[idx],CompairCommunityList[idx2])
                    if minValue >= currentNMI:
                        minValue = currentNMI
                    if maxValue <= currentNMI:
                        maxValue = currentNMI
                currentLineResult.append(currentNMI)
            ValidationMatrix.append(currentLineResult)
        
        ValidationMatrix = np.array(ValidationMatrix)
        
        # 画热力图
        column_labels = CommunityNameList
        row_labels = CommunityNameList  
        data = ValidationMatrix
        fig, ax = plt.subplots()
        #heatmap = ax.pcolor(data, cmap=plt.cm.Blues)
        
        # put the major ticks at the middle of each cell
        ax.set_xticks(np.arange(data.shape[0]), minor=False)
        ax.set_yticks(np.arange(data.shape[1]), minor=False)
        
        # want a more natural, table-like display
        ax.invert_yaxis()
        ax.xaxis.tick_top()
        
        ax.set_xticklabels(row_labels, minor=False)
        ax.set_yticklabels(column_labels, minor=False)
        
        ##加入色表
        from matplotlib import cm as CM
        cmap = CM.get_cmap(plt.cm.Blues,1000)
        map = ax.imshow(ValidationMatrix,interpolation = "nearest", cmap = cmap, aspect = 'auto', vmin = minValue, vmax = maxValue)
        cb = plt.colorbar(map)
        
        if ShowOrNot:
            plt.show()
        else:
            plt.savefig('heat map.png')
        
        return ValidationMatrix

if __name__ == '__main__':
    overlapping_set = [(16, 17, 20, 21, 15),\
        (37, 38, 39, 20, 21, 22, 23),\
        (25, 22, 23),\
        (20, 22, 23),\
        (24, 20, 21),\
        (21, 22, 23, 26, 27, 28),\
        (24, 26, 27, 28, 29),\
        (25, 26, 27, 28),\
        (9, 2, 5),\
        (11, 12, 7),\
        (19, 14, 15),\
        (10, 27, 26, 11, 28),\
        (34, 37, 38),\
        (11, 12, 6),\
        (27, 12, 28),\
        (26, 27, 28),\
        (3, 4, 5, 6, 7, 8, 9),\
        (11, 12, 15),\
        (36, 37, 38),\
        (0, 1, 2, 3, 4, 5, 6),\
        (32, 33, 34, 35, 36, 30, 31),\
        (33, 28, 29),\
        (3, 4, 5, 6, 7),\
        (17, 18, 12, 14),\
        (33, 34, 35, 36, 37, 38, 39),\
        (32, 26, 27, 28, 29, 30, 31),\
        (32, 33, 30, 31),\
        (37, 38, 39),\
        (1, 2, 37, 38),\
        (9, 11, 12),\
        (8, 11, 12),\
        (0, 37, 38),\
        (16, 11, 12),\
        (10, 11, 12, 13, 14, 15),\
        (16, 17, 13, 14, 15)]

    validation = Validation()

    independent_set = validation.DivideIndependentSet(overlapping_set)



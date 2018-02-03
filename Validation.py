#!/usr/bin/env python
#coding:utf-8
"""
  Author:  uniqueliu JHY
  Purpose: 在存在Ground Truth 的基础之上，评价当前社团划分结果的好坏:
    PART.1 需要 Ground Truth
        * CommunityQuality --- 社团质量
        * OverlapQuality --- 重叠节点质量
    PART.2 不需要Ground Truth
        * CommunityCoverage --- 社团覆盖率
        * OverlapCoverage --- 重叠覆盖率
  Created: 2016/7/16
"""
#@classmethod
#def DivideIndependentSet(cls, groups):
def DivideIndependentSet(groups):

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

#def NMI(self, Community1, Community2, isOverlapping=False):
def NMI(Community1, Community2, isOverlapping=False):

    """两个社团的互信息量
    输入：Community1 --- 社团1；Community2 --- 社团2
    输出：NMI Index
    """
    _MI = 0

    if isOverlapping:
        Community1 = DivideIndependentSet(groups=Community1)
        Community2 = DivideIndependentSet(groups=Community2)

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

########################################################################
class Validation_with_Ground_Truth:
    
    # 所有节点及其所在社团的标签信息
    # 结构: {node1:[label_1,label_2,label_3,...],...}
    __groundTruthLabel = {} 
    
    # 划分数据的节点及其所在社团的标签信息
    # 结构同__groundTruth 
    __communityLabel = {}
    
    # 当前划分结果
    __CommunityResult = []
    
    # 真实数据的所有点集
    __GT_nodes = [] # short for __Ground_Truth_Nodes
    
    # 划分数据的所有点集
    __C_nodes = [] # short for __Community_Result_Nodes
    
    
    #----------------------------------------------------------------------
    def __init__(self,groundTruthLabel,CommunityResult):
        self.__groundTruthLabel = groundTruth
        self.__CommunityResult = CommunityResult

        # 获取真实数据的所有点集
        self.__GT_nodes = list(set(node for node in groundTruth.keys()))
        
        # 获取划分数据的所有点集
        self.__C_nodes = set()
        for com in CommunityResult:
            self.__C_nodes.update(com)
        self.__C_nodes = list(self.__C_nodes)
        
        # 获取划分数据的社团标签信息，并构成诸如__groundTruth样式的字典
        # 这里采用划分结果的 索引 作为当前社团的标签
        for node in self.__C_nodes:
            for idx in range(len(self.__CommunityResult)):
                if node in self.__CommunityResult[idx]:
                    if node in self.__communityLabel:
                        self.__communityLabel[node].append(idx)
                    else:
                        self.__communityLabel[node] = [idx]
        
    #----------------------------------------------------------------------
    def __inSameLayer(self,node1,node2):
        """判断两节点是否在同一个社团内"""
        for com in self.__CommunityResult:
            if node1 in com and node2 in com:
                return True
        return False

    #----------------------------------------------------------------------
    def CommunityQuality(self):
        """计算社团质量, 并返回"""
        Community_Quality = 0
        
        GroundTruth_Similarity = 0
        # 计算GroundTruth下的两节点的相似性
        for _srcIdx in range(len(self.__GT_nodes)):
            for _dstIdx in range(srcIdx+1,len(self.__GT_nodes)):
                # 取出两个点
                src = self.__GT_nodes[_srcIdx]
                dst = self.__GT_nodes[_dstIdx]
                # 计算两点相似性
                GroundTruth_Similarity += len(set(self.__groundTruthLabel[src])&set(self.__groundTruthLabel[dst]))\
                    /len(set(self.__groundTruthLabel[src])|set(self.__groundTruthLabel[dst]))
        # 求平均
        GroundTruth_Similarity = GroundTruth_Similarity/(len(self.__GT_nodes)*(len(self.__GT_nodes)-1)*0.5)
        
        CommunityResult_Similarity = 0
        Community_edges = []
        # 计算CommunityResult下的两节点的相似性
        for _srcIdx in range(len(self.__C_nodes)):
            for _dstIdx in range(_srcIdx+1,len(self.__C_nodes)):
                src = self.__C_nodes[_srcIdx]
                dst = self.__C_nodes[_dstIdx]
                if self.__inSameLayer(src,dst):
                    CommunityResult_Similarity += len(set(self.__communityLabel[src])&set(self.__communityLabel[dst]))\
                        /len(set(self.__communityLabel[src])|self.__communityLabel[dst])
                # 保存边对信息
                if (src,dst) not in Community_edges and (dst,src) not in Community_edges:
                    Community_edges.append((src,dst))
                
        # 求平均
        CommunityResult_Similarity = CommunityResult_Similarity/len(Community_edges)
        
        Community_Quality = CommunityResult_Similarity/GroundTruth_Similarity
        return Community_Quality
    
    #----------------------------------------------------------------------
    def CommunityCoverage(self,graphs = None):
        """计算所有至少3个点组成的社团（即非平凡社团）覆盖率
        输入: graphs --- 所有网络  且若不传入该参数，则只计算多网络压缩成一个网络下是的覆盖率
        输出:
        Coverage --- 多网络压缩成一个网络下的 覆盖率
        AverageCoverage_perNetwork --- 每个网络的覆盖率 的平均
        """
        Coverage = 0
        AverageCoverage_perNetwork = 0
        
        # 取出所有非平凡社团下的所有点
        nodes = set()
        for com in self.__CommunityResult:
            if len(com)>= 3:
                nodes.update(com)
        
        Coverage = len(nodes)/len(self.__C_nodes)
        
        if graphs == None:
            AverageCoverage_perNetwork = None
        else :
            for graph in graphs:
                AverageCoverage_perNetwork += len(set(graph.nodes())&set(self.__C_nodes))/len(graph.nodes())
            AverageCoverage_perNetwork = AverageCoverage_perNetwork/len(graphs)

        return Coverage, AverageCoverage_perNetwork
    
    #----------------------------------------------------------------------
    def OverlapCoverage(self,graphs = None):
        """计算网络的重叠覆盖率
        输入: graphs --- 所有网络  且若不传入该参数，则只计算多网络压缩成一个网络下时的 重叠覆盖率
        输出:
        Overlap --- 多网络压缩成一个网络下的 重叠覆盖率
        Overlap_perNetwork --- 每个网络的 重叠覆盖率 的平均
        """
        Overlap = 0
        Overlap_perNetwork = 0
        
        nodes = set()
        for com in self.__CommunityResult:
            if len(com) >= 3:
                nodes.update(com)
        
        for node in nodes:
            Overlap += len(self.__communityLabel[node])
        
        Overlap = Overlap/len(nodes)
        
        if graphs == None:
            Overlap_perNetwork = None
        else:
            for graph in graphs:
                currentLayerOverlap = 0
                """注: 只计算非平凡点的Overlap信息!!!"""
                commonNodes = set(graph.nodes())&set(self.__C_nodes)
                for node in commonNodes:
                    currentLayerOverlap += len(self.__communityLabel[node])
                Overlap_perNetwork += currentLayerOverlap/len(commonNodes)

            Overlap_perNetwork = Overlap_perNetwork/len(graphs)
        
        return Overlap,Overlap_perNetwork


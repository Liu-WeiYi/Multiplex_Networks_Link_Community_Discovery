#!/usr/bin/env python
#coding:utf-8
import networkx as nx
"""
  Author:  uniqueliu --<>
  Purpose: 多网络社团发现中的Projection类方法
  Created: 2016/7/6
"""

########################################################################
class ProjectionMethods:
    """多网络社团发现中的Projection方法
    主要方法:
    1. Projection_Binary(Graphs) --- 二值化映射
    2. Projection_Average(Graphs) --- 平均化映射
    3. Projection_Neighbors(Graphs) --- 邻居映射
    """
    graphs = []
    # 二值化网络
    __one_binary_graph = nx.Graph()
    # 权值化网络
    __one_weighted_graph = nx.Graph()
    # 邻居相似性化网络
    __one_Neighbor_graph = nx.Graph()
    
    # 社团格式(假设共k个社团): {'Graph_layer_name':[[[c1],[c2],...,[ck]],modularity]}    
    Communities = {} 
    

    #----------------------------------------------------------------------
    def __init__(self,graphs):
        self.graphs = graphs
        self.__one_binary_graph = nx.Graph(name='All_In_One_Binary_Graph')
        self.__one_weighted_graph = nx.Graph(name='All_In_One_Weighted_Graph')
        self.__one_Neighbor_graph = nx.Graph(name='All_In_One_Neighbor_Graph')    
    
    #----------------------------------------------------------------------
    def __abstractingNeighbors(self,node,graphs):
        """提取所有网络 graphs 中某点 Node 的 邻居, 并返回"""
        neighbors = []
        for graph in graphs:
            if node in graph.nodes():
                neighbors.extend(graph.neighbors(node))
        neighbors = list(set(neighbors))# 去重
        return neighbors
    
    #----------------------------------------------------------------------
    def __showWeightedGraph(self,graph):
        """显示带权重的图"""
        pos = nx.spring_layout(graph)
        nx.draw_networkx_nodes(graph,pos,nodelist=graph.nodes(),node_size=600, node_color='g',alpha=0.5)
        # 提取所有带权重的边: 格式 --- weight_edge = (src,dst,weight)
        weight_edge_list = graph.edges(data='weight')
        weight_edge_dict = {}
        # 构造字典
        for weight_edge in weight_edge_list:
            weight_edge_dict[(weight_edge[0],weight_edge[1])] = weight_edge[2]
        nx.draw_networkx_edges(graph,pos,edgelist=graph.edges())
        nx.draw_networkx_edge_labels(graph,pos,edge_labels=weight_edge_dict)
        nx.draw_networkx_labels(graph,pos)
        
    #----------------------------------------------------------------------
    def Projection_Binary(self):
        """二值化映射方法"""
        self.__one_binary_graph = nx.Graph(name='All_In_One_Binary_Graph')
        for g in self.graphs:
            currentNodes = g.nodes()
            currentEdges = g.edges()
            self.__one_binary_graph.add_nodes_from(currentNodes)
            self.__one_binary_graph.add_edges_from(currentEdges)
        
        return self.__one_binary_graph
    
    #----------------------------------------------------------------------
    def Projection_Weight(self):
        """平均化权值方法
        平均化方法: 5片网络中存在3条同样的边，则这条边的权重为3/5
        """
        self.__one_weighted_graph = nx.Graph(name = 'All_In_One_Weighted_Graph')
        if self.__one_binary_graph.nodes() == []: # 并未生成二值网络
            currentGraph = self.Projection_Binary()
        else:
            currentGraph = self.__one_binary_graph
        
        # 给权值网络添加所有节点
        self.__one_weighted_graph.add_nodes_from(currentGraph.nodes())
        
        # 给权值网络添加所有边关系
        for edge in currentGraph.edges():
            currentWeight = 0
            for graph in self.graphs:
                if edge in graph.edges():
                    currentWeight += 1
            self.__one_weighted_graph.add_edge(edge[0],edge[1],weight=currentWeight)
        
        return self.__one_weighted_graph
    
    #----------------------------------------------------------------------
    def Projection_Neighbor(self):
        """邻居相似性的权值方法
        方法介绍: 采用两节点在多网络中相似性作为这两个节点的权重
        其中: 1. 两节点在多网络中的相似性用两节点在多网络中的公共邻居度量
             2. 一个节点在多网络中的邻居为其在每片网络中的邻居的并集
        """
        self.__one_Neighbor_graph = nx.Graph(name = 'All_In_One_Neighbor_Graph')
        if self.__one_binary_graph.nodes() == []: # 并未生成二值网络
            currentGraph = self.Projection_Binary()
        else:
            currentGraph = self.__one_binary_graph
        
        # 给邻居相似性网络添加所有节点
        self.__one_Neighbor_graph.add_nodes_from(currentGraph.nodes())
        
        # 给权值网络添加所有边关系
        for edge in currentGraph.edges():
            # 提取点关系
            nodeA,nodeB = edge[0],edge[1]
            # 获取点的邻居
            nodeA_Neighbor = self.__abstractingNeighbors(nodeA,self.graphs)
            nodeB_Neighbor = self.__abstractingNeighbors(nodeB,self.graphs)
            # 求相似性（采用Jaccard相似性系数）
            common_neighbor = list(set(nodeA_Neighbor) & set(nodeB_Neighbor))
            all_neighbor = list(set(nodeA_Neighbor) | set(nodeB_Neighbor))
            if all_neighbor != []:
                similarity = len(common_neighbor)/len(all_neighbor)
            else:
                similarity = 0
            # 添加这条边的权重信息
            self.__one_Neighbor_graph.add_edge(nodeA,nodeB,weight=similarity)
            
        return self.__one_Neighbor_graph
        
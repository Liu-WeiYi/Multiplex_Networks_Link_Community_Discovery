# coding: utf-8

# 导入内置模块
import copy
import time
import itertools
# 导入第三方模块
import networkx as nx
import matplotlib.pyplot as plt
# 导入自己的模块
from dendrogram import DendrogramGenerator


########################################################################
class Edge:
    """定义连边对结构体"""
    def __init__(self,n1,n2):
        if type(n1) == type(n2):
            if n1 < n2:
                self.__n1 = n1
                self.__n2 = n2
            else:
                self.__n1 = n2
                self.__n2 = n1
        else:
            if hash(n1) < hash(n2):
                self.__n1 = n1
                self.__n2 = n2
            else:
                self.__n1 = n2
                self.__n2 = n1            

        self.__name = '%s-%s'%(self.__n1,self.__n2)
            
    def __eq__(self, edge):
        if not isinstance(edge, Edge):
            return False
        elif type(self.__n1) != type(edge.__n1) or type(self.__n2) != type(edge.__n2):
            return False
        elif self.__n1 == edge.__n1 and self.__n2 == edge.__n2:
            return True
        else:
            return False
    
    def __hash__(self):
        return hash(self.__name)
    
    def __repr__(self):
        return self.__name
    
    def __str__(self):
        return self.__name
    
    def name():
        return self.__name
    
    def node(self):
        return self.__n1, self.__n2

class AbstractLinkCommnityDetectionAlgorithm:
    def __init__(self):
        pass

########################################################################
class MultiplexNetworkLinkCommnityDiscovery:
    """多网络连边检测社团发现"""
    """
    输入：
    graphs = [graph1,graph2,...,graphl]
    功能：
    1. 查找多网络中的所有连边对信息，注意，连边对是指在多网络中具有公共邻居的两条边的集合。共有两种形式，如下(以A-B-C为例)：
        CASE 1. 在 同层 网络中的公共邻居边对：(A-B-C,l1,l1)
        CASE 2. 在 不同层 网络中的公共邻居边对:(A-B---B-C,l1,l2)
    
    """
    """构造连边对的数据结构
        输入：
        edge1 --- 第一条边
        edge2 --- 第二条边
        CrossLayerPair --- 第一条边和第二条边所在的层，元组第一个元素表明第一条边所在网络层；第二个元素表明第二条边所在网络层
                       举例:CrossLayer = [(1,2),(2,3),(3,3)]表明e1和e2有两种关系：
                            CASE 1: (1,2) --- 第一层的e1和第二层的e2
                            CASE 2: (2,3) --- 第二层的e1和第三层的e2
                            CASE 3: (3,3) --- 第三层的e1和第三层的e2
        AllowLayerDuplication --- 是否考虑在某层中存在完整结构，而在其它层中不存在该结构（即下CASE 3），默认 不考虑（FALSE）
                       举例，重复层共有三种情况：
                            CASE 1: (e1,e2,L1,l1) --- 边e1和边e2在同一层 l1 上
                                     写成结构形式  --- (A-B-C,l1)
                            CASE 2: (e1,e2,l1,l2) --- 边e1在层 l1 上，边e2在层 l2 上
                                     写成结构形式  --- (A-B,l1, B-C,l2)
                            CASE 3: (e1,e2,l1,l1&l2) --- 边e1在层 l1 上，边e2 同时出现在层 l1 和 l2 上
                                     写成结构形式  --- (A-B-C,l1) & (A, B-C,l2)
                       注意：因为CASE3可以由CASE1和CASE2共同表征，所以在这里我们只考察第一种情况和第二种情况。

                       举例：假设两条边A-B,C-B所在层为: CrossLayerPair = [('l6','l6'),('l6','l1'), ('l6','l2'), ('l6','l4')]，有如下分析：
                            1. 该结构 A-B-C 存在在层l6上
                            2. 因为边A-B仅仅存在于层l6上，因此对于其它层，如果没有层l6的帮助下，无法形成A-B-C结构
                            3. 因此，该结构的属性：
                                                 __sameLayer = ['l6']
                                                 __NotSameLayerPair = []

    """

    graphs = []
    
    # 0. 根据每片网络的名称，生成字典，数据结构为：{'LayerName1':Graph1,'LayerName2':Graph2,...}
    __MultiplexGraphDict = {}
    
    # 1. 该多网络采用二值聚合后形成的单网络
    __oneGraph = nx.Graph(name = 'All in One Graph')
    
    # 2. 融合成的单网络中所有连边对, 数据结构为: [[Edge1,Edge2],...]
    __EdgePairs = []
    
    # 3. 该多网络的所有连边对
    __EdgePairViaLayers = []
    
    # 4. 该多网络中的所有边对的同层/跨层相似性，数据结构为: [[Edge1,Edge2,SameLayerSimilarity,CrossLayerSimilarity],...]
    #                                           Edge1,Edge2--- 由e1和e2构成的结构(e1-e2)
    #                                           SameLayerSimilarity ---  当前结构 (e1-e2) 由 同一层 组成时，这种情况下两条边的相似性
    #                                           CrossLayerSimilarity --- 当前结构 (e1-e2) 由 两层网络 组成时，该种情况下两条边的相似性
    __EdgePair_Same_Cross_Layer_similarity = []
    
    # 5. 该多网络中所有边对相似性，数据结构为: [[Edge1,Edge2,Similarity],...]
    __EdgePairSimilarity = []
    
    # 6. 最优划分结果
    __BestCommunity = []
    
    
    #----------------------------------------------------------------------
    def __init__(self,graphs):
        self.graphs = graphs
        start = time.time()
        
        """ 选择所需要的参数信息... """
        print('###################################')
        self.ConsiderCrossLayerFlag = False
        self.AllowLayerDulicationFlag = False
        
        """ 0. 根据每片网络的名称，生成多网络字典 """
        print(' 0. 根据每片网络的名称，生成多网络字典...')
        self.__MultiplexGraphDict = self.__GenerateMultiplexGraphDict(self.graphs)
        for graph in self.__MultiplexGraphDict:
            print(self.__MultiplexGraphDict[graph].name)
        print('###################################\n')
        
        """ 1. 将所有多网络融合成一个单网络 """
        print(' 1. 所有多网络融合成一个单网络...')
        self.__mergeGraphs(self.graphs)
        print(' 完成时间：%d秒'%(time.time()-start))
        
        
        """ 2. 提取合成的单网络的所有连边对 """
        print(' 2. 提取合成的单网络的所有连边对...')
        self.__EdgePairs, AllEdgeSets = self.__AbstractingConnectedEdgesFromOneGraph(self.__oneGraph)
        print(' 完成时间：%d秒'%(time.time()-start))
        start = time.time()
        
        """ 3. 计算连边对的 同层,跨层 相似性"""
        print(' 3. 计算连边对的 同层,跨层 相似性...')
        self.__EdgePair_Same_Cross_Layer_similarity = self.__CalculatingEdgePairSimilarity(self.__EdgePairs, self.graphs, False, False)
        
        print(' 完成时间：%d秒'%(time.time()-start))
        start = time.time()
        
        """
        -------------------------------------------------------------------------------
                --- 实验3 --- 
        统计所有的节点相似性，并画图
        """
        #import practise
        #practise.practise_three(self.__EdgePair_Same_Cross_Layer_similarity)
        
        """
                --- 实验3 结论 --- 
        一共有4670条边，SamelayerSimilarity 明显强于 CrossLayerSimilarity

        -------------------------------------------------------------------------------
        """ 
        
        """ 4. 构成树"""
        print(' 4. 构成树并进行分割...')
        self.__Dendrogram = DendrogramGenerator(self.__EdgePair_Same_Cross_Layer_similarity, AllEdgeSets)
        
        """ 5. 利用划分密度进行切割"""
        self.__DensityCurve = []
        
        self.__BestCommunity , self.__MaxDensity, self.__BestCutDepth= self.__Cut_DenDrogram_Multiplex_Network_based_on_Partition_Density(self.__Dendrogram,self.graphs)
        print(' 完成时间：%d秒'%(time.time()-start))
   
    #----------------------------------------------------------------------
    def __GenerateMultiplexGraphDict(self,Graphs):
        """ 根据多网络的名称，生成对应名称的多网络字典
        输入: Graphs --- 多网络列表
        输出格式: MultiplexGraphDict --- {'LayerName1':Graph1,'LayerName2':Graph2,...}
        注意: 如果传入的Graphs没有名字，则默认命名为['L1','L2','L3',...]
        输出: MultiplexGraphDict 
        """
        MultiplexGraphDict = {}
        for idx in range(len(Graphs)):
            if Graphs[idx].name == '':
                defaultName = 'L%d'%(idx+1)
            else:
                defaultName = Graphs[idx].name
            MultiplexGraphDict[defaultName] = Graphs[idx]
        
        return MultiplexGraphDict
    
    #----------------------------------------------------------------------
    def __mergeGraphs(self,graphs):
        """将所有多网络融合成一个单网络，采用二值化方法"""
        for graph in graphs:
            self.__oneGraph.add_nodes_from(graph.nodes())
            self.__oneGraph.add_edges_from(graph.edges())
    
    #----------------------------------------------------------------------
    def __AbstractingConnectedEdgesFromOneGraph(self,graph):
        """提取融合后的单网络中的所有具有公共邻居的边对
        """
        
        EdgePairs = set() # {(a,b,c)...}
        EdgeSet = set()
        for src, dst in graph.edges():
            for src_neighbors in graph.neighbors(src):
                if src_neighbors != dst:
                    EdgePairs.add((src_neighbors,src,dst,))

            for dst_neighbors in graph.neighbors(dst):
                if dst_neighbors != src:
                    EdgePairs.add((src,dst,dst_neighbors,))
            
            EdgeSet.add(Edge(src,dst))
    
        return list(EdgePairs), EdgeSet


    
    #----------------------------------------------------------------------
    def __CalculatingEdgePairSimilarity(self,EdgePairs, graphs, lamda = 0.5, AllowLayerDulicationFlag = False,ConsiderCrossLayerFlag = False):
        """通过分析每条边的行为，计算边对的跨网络相似性"""
        EdgePair_Similarity = []
        EdgePair_Same_Cross_Similarity = [] #[(Edge1, Edge2, s1, s2)...]
        
        for src,mid,dst in EdgePairs:
            
            # Case 1: complete src----mid----dst layers
            case1_src_neighbors = {src}
            case1_dst_neighbors = {dst}
            # Case 2: incomplete src--x--mid-----dst layers
            #          or        src-----mid--X--dst layers
            case2_src_neighbors = {src}
            case2_dst_neighbors = {dst}           
            for graph in self.graphs:
                if mid not in graph.nodes():
                    continue
                
                if src in graph.neighbors(mid) and dst in graph.neighbors(mid):
                    case1_src_neighbors.update(graph.neighbors(src))
                    case1_dst_neighbors.update(graph.neighbors(dst))
                    
                if src not in graph.neighbors(mid) and dst in graph.neighbors(mid):
                    case2_dst_neighbors.update(graph.neighbors(dst))

                if src in graph.neighbors(mid) and dst not in graph.neighbors(mid):
                    case2_src_neighbors.update(graph.neighbors(src))
                
            
            # Similarity
            same_layer_simi = len(case1_src_neighbors & case1_dst_neighbors)\
                /len(case1_src_neighbors | case1_dst_neighbors)
            cross_layer_simi = len(case2_src_neighbors & case2_dst_neighbors)\
                /len(case2_src_neighbors | case2_dst_neighbors)
            # 存储
            Edge1 = Edge(src, mid)
            Edge2 = Edge(mid, dst)
            EdgePair_Same_Cross_Similarity.append((Edge1,Edge2,same_layer_simi,cross_layer_simi))
            
            EdgePair_Similarity.append((Edge1,Edge2,lamda*same_layer_simi+(1-lamda)*cross_layer_simi))

        # 相似性排序并返回
        #EdgePair_Same_Cross_Similarity.sort(key=lambda x: x[2]+x[3], reverse=True)
        EdgePair_Similarity.sort(key=lambda x: x[2], reverse=True)
        
        return EdgePair_Similarity
    
    #----------------------------------------------------------------------
    def __EdgeBehaviorViaLayers(self,edge):
        """
        分析当前边在所有网络中是否存在
        并返回该边所在的所有层
        """
        layers = []
        src,dst = edge.node()
        for graph in self.graphs:
            if (src,dst) in graph.edges() or (dst,src) in graph.edges():
                # dst in graph.nodes() and src in graph.neighbors(dst)
                layers.append(graph.name)
        return layers
    
    #----------------------------------------------------------------------
    def __getCrossLayers(self,Edge1,Edge2,all_cross_layers,graphsDict):
        """
        去除CASE3
        """
        with_no_CASE3_Pairs = []
        
        for LayerPair in all_cross_layers:
            graph1 = graphsDict[LayerPair[0]]
            graph2 = graphsDict[LayerPair[1]]
            
            if graph1 == graph2:
                with_no_CASE3_Pairs.append(LayerPair)
            elif graph1 != graph2:
                
                Edge1Flag = Edge1.node() in graph1.edges() and Edge1.node() not in graph2.edges()
                Edge2Flag = Edge2.node() not in graph1.edges() and Edge2.node() in graph2.edges()
                if Edge1Flag & Edge2Flag:
                    with_no_CASE3_Pairs.append(LayerPair)

        return with_no_CASE3_Pairs
    
    #----------------------------------------------------------------------
    def __getPairSimilarityViaLayers(self,nodeA,nodeB,common,LayerPairs,ConsiderCrossLayerFlag = False):
        """获取两节点在层上的相似性
        输入: nodeA --- 节点A; nodeB --- 节点B; common --- 节点A和节点B的公共邻居
             LayerPairs --- 这两个节点对应边所在的层; 
             ConsiderCrossLayerFlag --- 即使当前节点所在边不在该层中出现，是否需要考虑该条边上的节点在该层上的邻居关系
        举例, 说明ConsiderCrossLayerFlag的意义:
        有边对(A-B,B-C),其中, A-B 在层 L3, L5 上; B-C 在层 L4, L6 上
        CASE 1: ConsiderCrossLayerFlag == True  --- N(A) = N(A,L3)|N(A,L4)|N(A,L5)|N(A,L6)
        CASE 2: ConsiderCrossLayerFlag == False --- N(A) = N(A,L3)|N(A,L5)
        """
        similarity = 0
        
        if len(LayerPairs) != 0:
            # 0. 初始化每一个节点所在层数
            nodeA_Graphs_layers = []
            nodeB_Graphs_layers = []
            
            # 1. 提取边所在层
            for layerPair in LayerPairs:
                nodeA_Graphs_layers.append(layerPair[0])
                nodeB_Graphs_layers.append(layerPair[1])
            # 1.1 是否需要考虑所有层
            if ConsiderCrossLayerFlag == True:
                nodeA_Graphs_layers = list(set(nodeA_Graphs_layers)|set(nodeB_Graphs_layers))
                nodeB_Graphs_layers = list(set(nodeA_Graphs_layers)|set(nodeB_Graphs_layers))
            
            # 2. 提取邻居
            nodeA_Neighbors = []
            nodeB_Neighbors = []
            nodeA_Neighbors.append(nodeA)
            nodeB_Neighbors.append(nodeB)
            for layer in list(set(nodeA_Graphs_layers)):
                if nodeA in self.__MultiplexGraphDict[layer]:
                    currentNeighbor = self.__MultiplexGraphDict[layer].neighbors(nodeA)
                    nodeA_Neighbors.extend(currentNeighbor)
            for layer in list(set(nodeB_Graphs_layers)):
                if nodeB in self.__MultiplexGraphDict[layer]:
                    currentNeighbor = self.__MultiplexGraphDict[layer].neighbors(nodeB)
                    nodeB_Neighbors.extend(currentNeighbor)
            # 2. 注明: 将当前节点在不同层中的同名邻居认为是一个邻居！
            #    比如: N(A,L1) = {B,C,D}; N(A,L2) = {B,C,E}; → N(A) = {B,C,D,E}; → N(A)+ = A|N(A) = {A,B,C,D,E}
            nodeA_Neighbors = list(set(nodeA_Neighbors))
            nodeB_Neighbors = list(set(nodeB_Neighbors))
            # 注意: 算公共邻居的时候应该包含节点自身
            nodeA_Neighbors.append(nodeA)
            nodeB_Neighbors.append(nodeB)
            
            # 3. 计算相似性
            CommonNeighbor = list(set(nodeA_Neighbors)&set(nodeB_Neighbors))
            CommonNeighbor.append(common)
            AllNeighbor = list(set(nodeA_Neighbors)|set(nodeB_Neighbors))
            AllNeighbor.append(common)
            if len(AllNeighbor) != 0:
                similarity = len(CommonNeighbor)/len(AllNeighbor)
            
        return similarity
    
    #----------------------------------------------------------------------
    def __Cut_DenDrogram_Multiplex_Network_based_on_Partition_Density(self,Dendrogram,graphs):
        """利用划分密度进行树划分"""
        bestCommunity = []
        max_D = 0
        BestCutDepth = -1
        maxdepth = 100 #Dendrogram.MaxDepth
        for depth in range(100):
            
            
            cut_simi = depth/maxdepth
            # 获取当前深度下的划分结果
            currentPartition = Dendrogram.GenerateCommunity(cut_simi_thr=cut_simi,least_com_num=1)
            
            current_D = 0
            
            for com in currentPartition:
                """ 1. 初始化该社团的所有层内边数、层间边数 """
                # 1. 该社团 每层边数之和 / 跨层边数之和
                com_Inner_Edges_Number = 0
                com_Cross_Edges_Number = 0
                
                # 2. 该社团 每层最小边数之和 / 跨层最小边数之和
                min_com_Inner_Edges_Number = 0
                min_com_Cross_Edges_Number = 0
                
                # 3. 该社团 每层最大边数之和 / 跨层最大边数之和
                max_com_Inner_Edges_Number = 0
                max_com_Cross_Edges_Number = 0
                
                """ 2. 计算层内边数 """
                com_Inner,min_com_Inner,max_com_Inner = self.__Count_Community_edges_per_Layers(com,graphs)
                com_Inner_Edges_Number += com_Inner
                min_com_Inner_Edges_Number += min_com_Inner
                max_com_Inner_Edges_Number += max_com_Inner
                
                """ 3. 计算层间边数 """
                com_Cross, min_com_Cross, max_com_Cross = self.__Count_Community_edges_Cross_Layers(com,graphs)
                com_Cross_Edges_Number +=com_Cross
                min_com_Cross_Edges_Number += min_com_Cross
                max_com_Cross_Edges_Number += max_com_Cross
                
                """ 4. 计算该社团在多网络内部的 总共边数、最小边数、最大边数 """
                com_edge_Number = com_Inner_Edges_Number + com_Cross_Edges_Number
                com_min_edge_Number = min_com_Inner_Edges_Number + min_com_Cross_Edges_Number
                com_max_edge_Number = max_com_Inner_Edges_Number + max_com_Cross_Edges_Number
                
                """ 5. 计算划分密度 """
                if com_max_edge_Number-com_min_edge_Number <= 0:
                    D_C = 0
                else:
                    D_C = (com_edge_Number-com_min_edge_Number)/(com_max_edge_Number-com_min_edge_Number)
                
                """ 6. 得出当前划分的划分密度评分结果 """
                current_D += com_edge_Number*D_C # 不用归一化。。。
            
            print('Cut depth %s//%s, Current group count%s'%\
                  (depth,maxdepth,len(currentPartition)))
            if current_D > max_D:
                    max_D = current_D
                    bestCommunity = currentPartition
                    BestCutDepth = depth
            self.__DensityCurve.append(current_D)
        
        return bestCommunity ,max_D, BestCutDepth
    
    #----------------------------------------------------------------------
    def __Count_Community_edges_per_Layers(self, com, graphs):
        """计算一个社团在多网络中所有层下的边数
        输入: com --- 当前边社团  graphs --- 所有网络
        输出: com_Inner, min_com_Inner, Max_com_Inner
        com_Inner --- 在所有层下该层社团的 总边数
        min_com_Inner --- 在所有层下该层社团的 最小 边数
        max_com_Inner --- 在所有层下该层社团的 最大 边数
        """
        com_Inner = 0
        min_com_Inner = 0
        max_com_Inner = 0
        
        # 提取当前边社团的点集
        current_com_nodes = []
        
        for edge in com:
            node1,node2 = edge.node()
            current_com_nodes.extend([node1,node2])
        current_com_nodes = list(set(current_com_nodes))
        
        # 遍历每张图，求边
        for graph in graphs:
            common_nodes = list(set(graph.nodes())&set(current_com_nodes))
            min_com_Inner += len(common_nodes)-1
            max_com_Inner += 0.5*len(common_nodes)*(len(common_nodes)-1)
            
            common_edges = []
            for node1_idx in range(len(common_nodes)):
                for node2_idx in range(node1_idx+1,len(common_nodes)):
                    node1 = common_nodes[node1_idx]
                    node2 = common_nodes[node2_idx]
                    if (node1,node2) in graph.edges() or (node2,node1) in graph.edges():
                        common_edges.append((node1,node2))
            com_Inner += len(list(set(common_edges)))
        
        return com_Inner, min_com_Inner, max_com_Inner
    
    #----------------------------------------------------------------------
    def __Count_Community_edges_Cross_Layers(self, com, graphs):
        """计算一个社团在多网络中所有层间的边数
        输入: com --- 当前边社团  graphs --- 所有网络
        输出: com_Cross, min_com_Cross, Max_com_Cross
        com_Cross --- 在所有层下该层社团的 总边数
        min_com_Cross --- 所有层之间的 该层社团的 最小 边数
        max_com_Cross --- 所有层之间的 该层社团的 最大 边数
        """
        com_Cross = 0
        min_com_Cross = 0
        max_com_Cross = 0
        
        min_com_Cross = 2*(len(self.graphs) - 1)
        
        for gIdx1 in range(len(graphs)):
            for gIdx2 in range(gIdx1+1,len(graphs)):
                max_com_Cross += self.__Count_pair_Layer_MAX_Cross_Edges_per_com(com,graphs[gIdx1],graphs[gIdx2])
                #min_com_Cross += self.__Count_pair_Layer_MIN_Cross_Edges_per_com(com,graphs[gIdx1],graphs[gIdx2])
                com_Cross += self.__Count_pair_Layer_Cross_Edges_per_com(com,graphs[gIdx1],graphs[gIdx2])
        
        return com_Cross,min_com_Cross,max_com_Cross
    
    #----------------------------------------------------------------------
    def __Count_pair_Layer_MAX_Cross_Edges_per_com(self,com,graph1,graph2):
        """计算一个社团在多网络中两层间的最大边数
        输入: com --- 当前边社团  graph1 --- 网络1  graph2 --- 网络2
        输出: max_Cross_Edges
        """
        max_Cross_Edges = 0
        current_com_nodes = []

        for edge in com:
            node1,node2 = edge.node()
            current_com_nodes.extend([node1,node2])
        current_com_nodes = list(set(current_com_nodes))
        
        max_Cross_Edges = len(set(graph1.nodes())&set(current_com_nodes)&set(graph2.nodes()))
        
        return max_Cross_Edges
    
    #----------------------------------------------------------------------
    def __Count_pair_Layer_MIN_Cross_Edges_per_com(self,com,graph1,graph2):
        """计算一个社团在多网络中两层间的 最小 边数
        输入: com --- 当前边社团  graph1 --- 网络1  graph2 --- 网络2
        输出: min_Cross_Edges
        """
        """注:
        一个社团在两层网络中的最小边数应该为该社团在两个网络中的最小生成树的最大匹配的最小值
        现阶段并不考虑
        """
        pass
        
    
    #----------------------------------------------------------------------
    def __Count_pair_Layer_Cross_Edges_per_com(self,com,graph1,graph2):
        """计算一个社团在多网络中两层间的 边数
        输入: com --- 当前边社团  graph1 --- 网络1  graph2 --- 网络2
        输出: Cross_Edges
        """
        
        same_behavior_node = set()
        for E in com:
            n1, n2 = E.node()
            if n1 in graph1.nodes() and n2 in graph1.neighbors(n1) and\
               n1 in graph2.nodes() and n2 in graph2.neighbors(n1):
                same_behavior_node.update((n1,n2,))
                
        return len(same_behavior_node)
    
    #----------------------------------------------------------------------
    def oneGraph(self):
        """返回所有多网络构成的单图"""
        return self.__oneGraph
    #----------------------------------------------------------------------
    def ConnectedNodesFromOneGraph(self):
        """返回所有具有公共邻居的连边的节点集合"""
        return self.__ConnectNodesFromOneGraph
    #----------------------------------------------------------------------
    def ConnectedEdgesFromOneGraph(self):
        
        """返回所有公共邻居连边对"""
        return self.__ConnectEdgesFromOneGraph
    
    def ConvertE2N(self, edge_coms):
        node_coms = []
        for com in edge_coms:
            com_node_set = set()
            for edge in com:
                com_node_set.update(edge.node())
            node_coms.append(tuple(com_node_set))
        return node_coms

    @property
    def EdgeCommunity(self):
        return self.__BestCommunity

    @property
    def NodeCommunity(self):
        return self.ConvertE2N(self.__BestCommunity)

    @property
    def DensityCurve(self):
        return self.__DensityCurve
        
    @property
    def MaxDensity(self):
        return self.__MaxDensity
    @property
    def Dendrogram(self):
        return self.__Dendrogram
        

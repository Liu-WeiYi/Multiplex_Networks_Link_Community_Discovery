import pandas as pd
import networkx as nx

class NoordinData:
    
    __NoordinAttrDF = None
    
    __NonadjacentNetnames = None

    def __init__(self,filename='Noordin Subset.xlsx'):
        '''
        构造函数
        参数：filename：文件名
        '''
        # Noordin 原始表格数据 pandas.DataFrame字典
        # { name: DataFrame, ...}
        self.__NoordinDFs = pd.read_excel(filename, sheetname=None)
        
        # Noordin Attribute数据, pandas.DataFrame对象
        self.__NoordinAttrDF = self.__NoordinDFs["13 Attributes"]
        
        # Noordin 邻接关系网络数据名字集合
        self.__AdjacentNetnames  = set(['2b Classmates', '4 Kinship', '8 Friendship', '9b Soulmates'])
        # Noordin 非邻接关系网络数据名字集合
        self.__NonadjacentNetnames = set(self.__NoordinDFs.keys()) - self.__AdjacentNetnames - {"13 Attributes"}
        
        self.__normalizeName()
        # 初始化 Noordin 网络
        self.__NoordinNodes = set(self.__NoordinDFs["13 Attributes"].index)
        self.__NoordinNets = dict()
        self.__NoordinNodes = set()
        self.__initGraph()
    
    def __normalizeName(self):
        '''
        对原始数据self.__NorrdinDFs进行名字纠正
        '''
        # 由于数据的名字里存在空格造成数据解析失败所以要对数据进行预处理
        nodes_index = self.__NoordinDFs["13 Attributes"].index
        normal_nodes_index = [s.strip() for s in nodes_index]
        
        # 修正 Attributes 表数据
        self.__NoordinDFs["13 Attributes"].index = normal_nodes_index
        
        # 修正邻接关系表数据表数据
        for name in self.__AdjacentNetnames:
            self.__NoordinDFs[name].index = normal_nodes_index
            self.__NoordinDFs[name].columns = normal_nodes_index
        
        # 修正非邻接关系表数据表数据
        for name in self.__NonadjacentNetnames:
            self.__NoordinDFs[name].index = normal_nodes_index
    def __initGraph(self):
        '''
        初始化Noordin网络数据
        '''
        # 初始化邻接网络
        for name in self.__AdjacentNetnames:
            net = nx.Graph(name=name)
            tdf = self.__NoordinDFs[name]
            for col in tdf.columns:
                a = tdf[tdf[col]==1].index
                if len(a) == 0:
                    continue
                else:
                    a = list(a)
                    a.insert(0,col)
                    net.add_star(a)
            self.__NoordinNets[name] = net
        
        #初始化非邻接网络
        for name in self.__NonadjacentNetnames:
            net = nx.Graph(name=name)
            tdf = self.__NoordinDFs[name]
            for col in tdf.columns:
                nodes = tdf[tdf[col]==1].index
                for x in range(len(nodes)-1):
                    for y in range(x+1,len(nodes)):
                        net.add_edge(nodes[x],nodes[y])
            self.__NoordinNets[name] = net
            
    def GetNoordinAttr(self):
        '''
        获取Noordin Attribute表数据
        返回: pandas.DataFrame 对象
        '''
        return self.__NoordinAttrDF
    
    def DrawNet(self, name, isShowing=True):
        '''
        画一个指定名字name的网络，并保存在当前文件夹
        参数:
        name: 网络名字
        isShowing:是否画出来
        '''
        DrawOneNet(self.__NoordinNets[name],isShowing)
        
    def GetAdjNames(self):
        '''
        获取邻接表网络名字集合
        返回：名字集合
        '''
        return self.__AdjacentNetnames
    
    def GetNonAdjNames(self):
        '''
        获取非邻接表网络名字集合
        返回：名字集合
        '''        
        return self.__NonadjacentNetnames
    
    def GetNames(self):
        '''
        获取所有网络名字集合
        返回：名字集合
        '''        
        return self.__NonadjacentNetnames.union(self.__AdjacentNetnames)
    
    def GetNets(self, name=None):
        '''
        获取nx.Graph网络数据
        参数：
        name: 网络名字, 若为None返回所有网络
        返回：nx.Graph网络对象或对象字典
        '''
        if name is None:
            return self.__NoordinNets
        else:
            return self.__NoordinNets[name]
        
    def GetOrignalDFDict(self):
        '''
        返回原始DatFrame字典数据
        '''
        return self.__NoordinDFs
    #----------------------------------------------------------------------
    def CombineNet(self, output_name,input_names):
        '''
        合并网络
        参数:
        output_name: 合并后的网络名字
        input_names: 需要合并的网络名字
        返回: nx.Graph 对象
        '''
        net = nx.Graph(name=output_name)
        net.add_nodes_from(self.__NoordinNodes)
        for n in input_names:
            net.add_edges_from(self.__NoordinNets[n].edges())
        
        return net
    
    
    _t_cnt = 0 #图标号的辅助变量
    @classmethod
    def DrawOneNet(cls, net, isShowing = True):
        '''
        画一个网络
        '''
        import matplotlib.pyplot as plt
        
        if net.name is "":
            name = 'net%d'%_t_cnt
            _t_cnt += 1
        else:
            name = net.name
        pos = nx.spring_layout(net)
        plt.figure(name)
        plt.title('%s, nodes:%d, edges:%d'%(name, len(net.nodes()), len(net.edges())))
        nx.draw_networkx_nodes(net,pos,node_color='b',node_size = 300,alpha=0.5)
        nx.draw_networkx_edges(net,pos,style='dashed')
        nx.draw_networkx_labels(net,pos,font_size=10)
        plt.savefig(name+'.png', dpi=200)
        if isShowing: plt.show()     
        pass    

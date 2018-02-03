import sys

import matplotlib.pyplot as plt
import networkx as nx

import manualnetwork
import Link_Community_Discovery

from pylouvain import LouvainCommunities

class NetworkAnalyzer:
    def __init__(self, netObj):
        # nx.Graph object.
        self.net = None
        
        # modularity attribution
        self.__isModularityAna = False
        self.__modularity = None    # numerical
        self.__modularityCommunity = None   # [(..), (..)...]
        # link detection attribution
        self.__isLinkDAna = False
        self.__densityCurve = None  # numerical list 
        self.__maxdensity = None    # numerical
        self.__linkEdgeCommunity = None # [(..), (..)...]
        self.__linkNodeCommunity = None # [(..), (..)...]
        
        if isinstance(netObj, str):
            import pickle
            self.net = pickle.load(netObj)
        elif isinstance(netObj, nx.Graph):
            self.net = netObj
            
        self.__node_num = len(self.net.nodes())
        self.__edge_num = len(self.net.edges())
        
        pass
    
    
    def ModularityAnalysis(self):
        self.__isModularityAna = True
        communities , modularity = LouvainCommunities(self.net)
        self.__modularityCommunity = communities
        self.__modularity = modularity
        
        label = 0
        for each_com in communities:
            _attr = {x:str(label) for x in each_com}
            nx.set_node_attributes(self.net, 'LouvainCom', _attr)
            label += 1
        pass
    
    def LinkDetectionAnalysis(self):
        self.__isLinkDAna = True
        lcd = Link_Community_Discovery.MonoplexNetworkLinkCommunityDiscovery(self.net,False)
        self.__maxdensity = lcd.MaxDensity
        self.__densityCurve = lcd.DensityCurve
        self.__linkEdgeCommunity = lcd.EdgeCommunity
        self.__linkNodeCommunity = lcd.NodeCommunity
        label = 0
        for each in lcd.EdgeCommunity:
            _attr = {e.node():str(label) for e in each}
            nx.set_edge_attributes(self.net, 'LinkCom', _attr)
            label += 1
        pass
    
    def Analysis(self):
        if not self.__isModularityAna:
            self.ModularityAnalysis()
            
        if not self.__isLinkDAna:
            self.LinkDetectionAnalysis()

        nx.write_gml(G=self.net, path='%s.gml'%self.net.name, stringizer=lambda x :str(x) if isinstance(x,int) else x)
        pass
    
    def TextResult(self, fileObj=sys.stdout):
        
        self.Analysis()
        print('-----------------------------START------------------------\n',file=fileObj)
        print('### Abstract: ###\n', file=fileObj)
        print(nx.info(self.net), file=fileObj)
        
        print('### Modularity Info: ###\n', file=fileObj)
        print('Modularity: %s'%self.__modularity, file=fileObj)
        print('#### Community: ####\n', file=fileObj)
        label = 0
        for each_com in self.__modularityCommunity:
            _info = 'Community %s\'s info: \tnode number: %s,\t%.4f%%\n'\
                %(label,\
                  len(each_com),\
                  len(each_com)/self.__node_num)
            
            print(_info, file=fileObj)
            print(each_com, file=fileObj)
            print('',  file=fileObj)
            label += 1
            
        print('### Link detection Info: ###\n', file=fileObj)
        print('Maximun Link Desity: %.4f\n'%self.__maxdensity, file=fileObj)
        label = 0
        for each_edge_com, each_node_com in zip(self.__linkEdgeCommunity, self.__linkNodeCommunity):
            _info = 'Community %s\'s info: \tEdge number: %s,\t%.4f%%\tNode number: %s,\t%.4f%%\n'\
                %(label,\
                  len(each_edge_com),\
                  len(each_edge_com)/self.__edge_num,\
                  len(each_node_com),\
                  len(each_node_com)/self.__node_num)
            print(_info,  file=fileObj)
            print(each_edge_com, file=fileObj)
            print(each_node_com, file=fileObj)
            print('',  file=fileObj)
            label += 1
        print('-----------------------------END------------------------\n',file=fileObj)
        fileObj.flush()
        pass
    
    def VizResult(self, isShow=False):
        
        self.Analysis()
        manualnetwork.DrawOneNet(net=self.net, isShowing=False)
        plt.figure('Density Curve')
        plt.plot(self.__densityCurve)
        plt.savefig(self.net.name+'_Density Curve'+'.png', dpi=200)
        if isShow:
            plt.show()
        pass
    
    def Result(self,fileObj=sys.stdout, isShow=False):
        self.TextResult(fileObj=fileObj)
        self.VizResult(isShow=False)
        pass
    

if __name__ == '__main__':
    nets = manualnetwork.WSCommunityNetworks(net_num=2, node_num=40, group_num=2, overraping=10, neighbor=11, p=0.1, reduncy_edge_num=2)
    cnet = manualnetwork.CombineNet('cnet', nets)
    analyzer = NetworkAnalyzer(netObj=cnet)
    analyzer.Analysis()
    analyzer.Result(fileObj=open('result.txt','w'), isShow=False)
    

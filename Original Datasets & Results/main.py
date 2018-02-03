# coding: utf-8

import matplotlib.pyplot as plt
import pickle
import networkx as nx

'''
TEST Multiplex Graphs
Layers Number: 6
Nodes Number: 5
'''
import TEST_MULTIPLEX_GRAPHS as testGraph
#graphs = testGraph.GenerateGraph()
graphs = testGraph.ReadGraphs()
#testGraph.ShowGraphs(graphs)

#'''
#Call Link_Community_Discovery
#'''
#import Link_Community_Discovery
#MN_LC = Link_Community_Discovery.MultiplexNetworkLinkCommnityDiscovery(graphs)

"""
Call Projection Method
"""
import ProjectionType_Multiplex_Community_Discovery as P_MCD
import pylouvain as pL
# Analysis Binary_NET related Works
Binary_Net = P_MCD.ProjectionMethods(graphs).Projection_Binary()
Binary_Communities,Modularity = pL.LouvainCommunities(Binary_Net)
#print(Binary_Communities)
print(Modularity)

# Analysis Weighted Net Related Works
Weight_Net = P_MCD.ProjectionMethods(graphs).Projection_Weight()
Weight_Communities,Modularity = pL.LouvainCommunities(Weight_Net)
#print(Weight_Communities)
#print(Modularity)

# Analysis Neighbors_NET related Works
Neighbor_Net = P_MCD.ProjectionMethods(graphs).Projection_Neighbor()
Neighbor_Communities,Modularity = pL.LouvainCommunities(Neighbor_Net)
#print(Neighbor_Communities)
#print(Modularity)

"""
Ground Truth...
"""
with open('Community_Ground_Truth.pickle','rb') as f:
    Community_Ground_Truth = pickle.load(f)

"""
NMI Calculation
"""
from CommunityValidation import *
#Binary_Validation = Validation().NMI(Binary_Communities,Community_Ground_Truth)

communities = [Binary_Communities,Weight_Communities,Neighbor_Communities,Community_Ground_Truth]
Result = Validation().CompairValidationHeatMap(['Binary','Weighted','Neighbor','GroundTruth'],communities,'NMI',False)

"""
Modularity Compare
"""
for com in communities:
    # On Monoplex Graph
    o = Validation().Modularity(com,Binary_Net)
    # On Multiplex Graphs
    m = Validation().Modularity(com,graphs)
    print('On Monoplex Graph: %.4f\tOn Multiplex Graphs: %.4f'%(o,m))

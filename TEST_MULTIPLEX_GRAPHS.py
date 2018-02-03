# coding: utf-8
import matplotlib.pyplot as plt
import networkx as nx
import pickle

def GenerateGraph():
    Node_list = ['A','B','C','D']

    Graph1 = nx.Graph(name = 'Layer1')
    Graph1_edges = [('A','B'),('A','D'),('C','B')]
    Graph1.add_nodes_from(Node_list)
    Graph1.add_edges_from(Graph1_edges)
    
    Graph2 = nx.Graph(name = 'Layer2')
    Graph2_edges = [('A','B'),('C','D'),('C','B')]
    Graph2.add_nodes_from(Node_list)
    Graph2.add_edges_from(Graph2_edges)
    
    Graph3 = nx.Graph(name = 'Layer3')
    Graph3_edges = [('A','B'),('B','D'),('C','D')]
    Graph3.add_nodes_from(Node_list)
    Graph3.add_edges_from(Graph3_edges)
    
    Graph4 = nx.Graph(name = 'Layer4')
    Graph4_edges = [('A','D'),('B','D'),('C','B')]
    Graph4.add_nodes_from(Node_list)
    Graph4.add_edges_from(Graph4_edges)
    
    Graph5 = nx.Graph(name = 'Layer5')
    Graph5_edges = [('A','B'),('C','D')]
    Graph5.add_edges_from(Graph5_edges)
    Graph5.add_nodes_from(Node_list)
    
    Graph6 = nx.Graph(name = 'Layer6')
    Graph6_edges = [('A','C'),('B','D'),('C','B')]
    Graph6.add_nodes_from(Node_list)
    Graph6.add_edges_from(Graph6_edges)
    
    return [Graph1,Graph2,Graph3,Graph4,Graph5,Graph6]

#----------------------------------------------------------------------
def ReadGraphs():
    """读入恐怖组织的所有网络"""
    with open('net_dict.pickle','rb') as f:
        network_dict = pickle.load(f)
    graphs = []
    for graph in network_dict:
        graphs.append(network_dict[graph])
    return graphs

#----------------------------------------------------------------------
def ShowGraphs(Graphs):
    """展示所有图"""
    for g in Graphs:
        plt.figure(g.name)
        pos = nx.spring_layout(g)
        nx.draw_networkx_nodes(g, pos, node_size=300,node_color='b',alpha=0.8)
        nx.draw_networkx_edges(g,pos)
        nx.draw_networkx_labels(g,pos)
    
    plt.show()
    
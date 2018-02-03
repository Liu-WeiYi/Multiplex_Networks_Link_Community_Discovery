#!/usr/bin/env python
#coding:utf-8
"""
  Author:  LWY --<>
  Purpose: 画图
  Created: 2016/7/10
"""
import pickle
Results = pickle.load(open('All_Combination_Results.pickle','rb'))
import matplotlib.pyplot as plt
import networkx as nx




for re in range(1,15):
    plt.figure(re)
    graph = Results[re][0][2]
    nx.draw(graph)
    # 输出 GEXF 文件
    nx.write_gexf(graph,'%d.gexf'%re)
    
    plt.savefig('%d.png'%re)
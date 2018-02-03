#!/usr/bin/env python
#coding:utf-8
"""
  Author:  uniqueliu JHY --<>
  Purpose: 实现若干实验方法
  Created: 2016/7/10
"""
import itertools
import pickle

import ProjectionType_Multiplex_Community_Discovery as P_MCD
import pylouvain

#----------------------------------------------------------------------
def practise_one(graph_names,graphs):
    """实现14种网络中选6个网络进行融合，并计算模块度
    输入: graph_names --- 所有网络的名称集合 graphs --- 所有网络的字典
    输出: max_modularity, currentCombination
    
    """
    print(' --- 进行 practise one 实验 ---')

    # max_modularity --- 最大的模块度
    # currentCombination --- 当前最大模块度下的网络组合    
    
    max_modularity = 0
    currentCombination = []
    
    all_combination = list(itertools.combinations(graph_names,6))
    print('all combination number: %d'%len(all_combination))
    count = 0
    
    for combine in all_combination:
        print('current combination: %d'%count)
        count += 1
        
        # 获取当前组合下的6张网络
        current_graphs = []
        for name in combine:
            current_graphs.append(graphs[name])
        Binary_Net = P_MCD.ProjectionMethods(current_graphs).Projection_Binary()
        # 计算模块度
        com,modularity = pylouvain.LouvainCommunities(Binary_Net)
        # 判断大小
        if modularity > max_modularity:
            max_modularity = modularity
            currentCombination = combine
    
    print('max_modularity: %.4f\tCurrentCombination: %s'%(max_modularity,str(currentCombination)))
    print('----------------------------------------------------------------------')

        
#----------------------------------------------------------------------
def practise_two(graph_names,graphs):
    """实现14种网络中选i个网络进行融合，并计算模块度
    输入: graph_names --- 所有网络的名称集合 graphs --- 所有网络的字典
    输出: max_modularity, currentCombination
    
    """
    print(' --- 进行 practise two 实验 ---')
    
    import time
    start = time.time()

    results = {}

    for i in range(1,15):
        print('Calculating Combination :%d'%i)
        
        results[i] = []

        max_modularity = 0
        currentCombination = []
        
        all_combination = list(itertools.combinations(graph_names,i))
        print('all combination number: %d'%len(all_combination))
        count = len(all_combination)
        
        for combine in all_combination:
            if count % 100 == 0 and i != 1:
                print('current combination: %d'%count)
            elif i == 1:
                print('current combination: %d'%count)
            
            count -= 1
            
            # 获取当前组合下的i张网络
            current_graphs = []
            for name in combine:
                current_graphs.append(graphs[name])
            Binary_Net = P_MCD.ProjectionMethods(current_graphs).Projection_Binary()
            # 计算模块度
            com,modularity = pylouvain.LouvainCommunities(Binary_Net)
            # 判断大小
            if modularity > max_modularity:
                max_modularity = modularity
                currentCombination = combine
        
        # 存储当前结果
        results[i].append([max_modularity,currentCombination,Binary_Net])
        
        print('currentCombinationNumber:%d\tmax_modularity: %.4f\tCurrentCombination: %s'\
              %(i,max_modularity,str(currentCombination)))
    
    # 存储所有结果
    with open('结果\\All_Combination_Results.pickle','wb') as f:
        pickle.dump(results,f)
    
    print('cost time: %s (s), %s (min)'%(str(time.time()-start),str((time.time()-start)/60)))
    print('----------------------------------------------------------------------')
    
#----------------------------------------------------------------------
def practise_three(EdgePairSimilarity):
    """
    输入: EdgePairSimilarity --- [[Edge1,Edge2],SameLayerSimilarity,CrossLayerSimilarity],...]
    输出: 所有连边对的SameLayerSimilarity和CrossLayerSimilarity"""
    
    SameSimilarityFile = open('结果\\Same_Similarity.txt','w+')
    CrossSimilarityFile = open('结果\\Cross_Similarity.txt','w+')
    
    for EdgePair in EdgePairSimilarity:
        Edge1,Edge2,SameSimilarity,CrossSimilarity = EdgePair
        
        SameSimilarityFile.write(str(SameSimilarity)+'\n')
        CrossSimilarityFile.write(str(CrossSimilarity)+'\n')
    
    SameSimilarityFile.close()
    CrossSimilarityFile.close()


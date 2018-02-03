#!/usr/bin/env python
#coding:utf-8
"""
  Author:  uniqueliu --<>
  Purpose: 分析三种相似性的分布情况
  Created: 2016/7/8
"""
import pickle
EdgePairSimilarity = pickle.load(open('EdgePairSimilarities.pickle','rb'))

#SameLayerSimilarity = []
#CrossLayerSimilarity = []

SameLayerSimilarityFile = open('SameLayerSimilarityFile.txt','w+')
CrossLayerSimilarityFile = open('CrossLayerSimilarityFile.txt','w+')

for pair in EdgePairSimilarity:
    #SameLayerSimilarity.append(pair[1])
    SameLayerSimilarityFile.write(str(pair[1])+'\n')
    #CrossLayerSimilarity.append(pair[2])
    CrossLayerSimilarityFile.write(str(pair[2])+'\n')
    
SameLayerSimilarityFile.close()
CrossLayerSimilarityFile.close()
    


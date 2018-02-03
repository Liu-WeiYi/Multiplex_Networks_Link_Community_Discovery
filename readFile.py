import numpy as np

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from sklearn.decomposition import PCA

import noordindata


print('Loading excel data')
noor = noordindata.NoordinData(filename='Noordin Subset.xlsx')

# 属性DataFrame对象
noor_attr_df = noor.GetNoordinAttr()

col_data_dict = {}

for col in noor_attr_df.columns:
    data_set = list(set(noor_attr_df[col]))
    data_set.sort()
    data_len = len(data_set)
    col_data_dict[col] = {x:y for x,y in zip(data_set, range(data_len))}
    

print('Converting data')
all_data_vec = []

for idx in noor_attr_df.index:
    vec = []
    for col in noor_attr_df.columns:
        label = noor_attr_df[col][idx]
        col_vec = [0]*len(col_data_dict[col])
        col_vec[col_data_dict[col][label]] = 1
        vec.extend(col_vec)
    all_data_vec.append(vec)

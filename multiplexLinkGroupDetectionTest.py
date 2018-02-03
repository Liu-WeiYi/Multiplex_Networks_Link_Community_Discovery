import os
import json
import pickle
import matplotlib.pyplot as plt
import networktest
import manualnetwork
import Link_Community_Discovery

filename = 'multiplexnets.pickle'

if os.path.exists(filename):
    nets = pickle.load(open(filename,'rb'))
else:
    nets = manualnetwork.WSCommunityNetworks(net_num=2, node_num=40, group_num=2, overraping=10, neighbor=6, p=0.1, reduncy_edge_num=2)
    pickle.dump(nets,open(filename,'wb'))

cnet = manualnetwork.CombineNet('cnet', nets)
analyzer = networktest.NetworkAnalyzer(netObj=cnet)
analyzer.Analysis()
analyzer.Result(fileObj=open('result.txt','w'), isShow=False)

mnlcd = Link_Community_Discovery.MultiplexNetworkLinkCommnityDiscovery(nets)

htree = mnlcd.Dendrogram

s = htree.Serialize()

json.dump(s, open('tree.dat','w'))


densityCurve = mnlcd.DensityCurve

best_cut = -1
max_density = -1
idx = 0
for x in densityCurve:
    if x > max_density:
        best_cut = idx
        max_density = x
    idx += 1
    
print(best_cut,max_density)

root = htree.RootNode


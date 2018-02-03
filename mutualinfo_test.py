import matplotlib.pyplot as plt
from CommunityValidation import Validation
import manualnetwork
from networktest import NetworkAnalyzer
import Link_Community_Discovery
from dendrogram import DendrogramGenerator

nets = manualnetwork.WSCommunityNetworks\
    (net_num=2, node_num=40, group_num=2,\
     overraping=10, neighbor=11, p=0.1,\
     reduncy_edge_num=2)
cnet = manualnetwork.CombineNet('cnet', nets)
#analyzer = NetworkAnalyzer(netObj=cnet)
#analyzer.Analysis()
#analyzer.Result(fileObj=open('result.txt', 'w'), isShow=False)

realCommunity = []
realCommunity.append([x      for x in range(10)])
realCommunity.append([x + 10 for x in range(10)])
realCommunity.append([x + 20 for x in range(10)])
realCommunity.append([x + 30 for x in range(10)])

validation = Validation()
mnlcd = Link_Community_Discovery.MultiplexNetworkLinkCommnityDiscovery(nets)
snlcd = Link_Community_Discovery.MultiplexNetworkLinkCommnityDiscovery([cnet])

mn_groups = [x for x in mnlcd.NodeCommunity if len(x)>2]
sn_groups = [x for x in snlcd.NodeCommunity if len(x)>2]

nmi_mnlcd = validation.NMI(realCommunity, mn_groups, True)
nmi_snlcd = validation.NMI(realCommunity, sn_groups, True)
nmi_mutual = validation.NMI(mn_groups, sn_groups, True)

mn_cut_sets = validation.DivideIndependentSet(mn_groups)
sn_cut_sets = validation.DivideIndependentSet(sn_groups)

print('---------------------------------')
print('mn_cut_sets result')
for group in mn_cut_sets:
    print(group)

print('sn_cut_sets result')
for group in sn_cut_sets:
    print(group)
print('---------------------------------')
print('nmi_mnlcd = %.7f'%nmi_mnlcd)
print('nmi_snlcd = %.7f'%nmi_snlcd)
print('nmi_mutual = %.7f'%nmi_mutual)



htree = mnlcd.Dendrogram

nmi_seqs = []
for x in range(100):
    cut_thr = x/100

    groups = DendrogramGenerator.ConvertE2N(htree.GenerateCommunity(cut_thr,2))

    nmi = validation.NMI(realCommunity, groups, True)
    nmi_seqs.append(nmi)
    print('-------------------------------------------------')
    for group in groups:
        print(group)
    print(" Cut threshold = %.3f, mutual information = %.5f"%(cut_thr, nmi))




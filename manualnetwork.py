from random import randint
import networkx as nx
import matplotlib.pyplot as plt

def CombineNet(output_name,nets):
    '''
    合并网络
    参数:
    output_name: 合并后的网络名字
    input_names: 需要合并的网络名字
    返回: nx.Graph 对象
    '''
    new_net = nx.Graph(name=output_name)
    for net in nets:
        new_net.add_edges_from(net.edges())
    return new_net

def DrawOneNet(net, isShowing = True):
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
    nx.draw_networkx_labels(net,pos,font_size=35)
    plt.savefig(name+'.png', dpi=200)
    if isShowing: plt.show()     
    pass 

def WSCommunityNetworks(net_num, node_num, group_num, overraping, neighbor, p, reduncy_edge_num):

    multiplex_nets = []
    if node_num % group_num is 0:
        node_num_per_com = node_num // group_num
    else:
        node_num_per_com = node_num // group_num + 1

    for net_idx in range(net_num):
        remain_node_num = node_num
        net = nx.Graph(name=str(net_idx))
        reduncy_edges = set()
        for group_idx in range(group_num):

            real_com_node_num = min(node_num_per_com, remain_node_num)
            WS = nx.random_graphs.watts_strogatz_graph(real_com_node_num, neighbor, p)
            index_offset = group_idx * node_num_per_com + net_idx * overraping

            ws_edges = [((x[0]+index_offset)%node_num, (x[1]+index_offset)%node_num) for x in WS.edges()]
            net.add_edges_from(ws_edges)

            _x = reduncy_edge_num
            while(_x > 0):
                n1 = randint(0,real_com_node_num-1)
                n2 = randint(real_com_node_num,node_num-1)
                e = ((n1+index_offset)%node_num, (n2+index_offset)%node_num)
                er= ((n2+index_offset)%node_num, (n1+index_offset)%node_num)
                if ( e in reduncy_edges or er in reduncy_edges):
                    continue
                reduncy_edges.add(e)
                _x -= 1

        net.add_edges_from(reduncy_edges)
        multiplex_nets.append(net)

    return multiplex_nets

if __name__ == '__main__':
    nets = WSCommunityNetworks(net_num=2, node_num=20, group_num=2, overraping=5, neighbor=6, p=0.1, reduncy_edge_num=2)
    for net in nets:
        DrawOneNet(net=net, isShowing=True)
    cnet = CombineNet('c_net',nets)
    DrawOneNet(net=cnet, isShowing=True)
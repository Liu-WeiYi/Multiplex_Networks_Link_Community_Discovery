class TreeNode:
    Cnt = 0
    def __init__(self, info="node", simi = 0.0, parent=None):
        self.parent = parent
        self.info = info
        self.children = []
        TreeNode.Cnt += 1
        self.Depth = 0
        self.simi = simi
    def AddChild(self, child):
        self.children.append(child)
    def AddChildren(self, children):
        self.children.extend(children)
    def Setparent(self, parent):
        self.parent = parent

class DendrogramGenerator:
    """docstring for DendroGram"""

    @classmethod
    def __findTree(cls, forest, node):
        for tree in reversed(forest):
            if node in tree[1]:
                return tree
        return None

    @classmethod
    def __CutTree(cls, tree, cut_simi):
        
        assert(cut_simi >= -0.001)
        curr_forest = [tree]
        cut_well_trees = []
        is_continue_cut = True
        while is_continue_cut:
            is_continue_cut = False
            next_forest = []
            for tree in curr_forest:
                if tree.simi < cut_simi:
                    next_forest.extend(tree.children)
                    is_continue_cut = True
                else:
                    cut_well_trees.append(tree)
            
            curr_forest = next_forest
        
        return cut_well_trees

    def __init__(self, node_pairs_data, node_set):
        self.__node_pairs_data = node_pairs_data
        self.__node_set = node_set
        self.__leaves_info = dict()
        self.__root = self.__GenerateTree()
        pass


    def __GenerateTree(self):
        '''
        生成树状图
        参数：
        pairs_data: [(a1,b1),(a2,b2)...]
        nodes: 节点集
        '''
        
        # 森林 [(TreeNode,(nodes..),...]
        forest = [(TreeNode(n, 1.0), {n}) for n in self.__node_set]

        for tree in forest:
            self.__leaves_info[tree[0]] = tuple(tree[1])
            
        for pair in self.__node_pairs_data:
            if abs(pair[2]) < 0.0001 or len(forest) is 1:
                break
            tree1 = DendrogramGenerator.__findTree(forest, pair[0])
            tree2 = DendrogramGenerator.__findTree(forest, pair[1])
            if tree1 is tree2:
                continue
            
            if abs(tree1[0].simi - tree2[0].simi) < 0.00001 and (tree1[0].info == 'inner' or tree2[0].info == 'inner'):
                # 两棵树相似性相同
                remain_tree = tree1 if tree1[0].info == 'inner' else tree2
                left_tree   = tree2 if tree1[0].info == 'inner' else tree1
                
                remain_tree[0].AddChildren(left_tree[0].children)
                remain_tree[1].update(left_tree[1])
                
                self.__leaves_info[remain_tree[0]] = tuple(remain_tree[1])
                self.__leaves_info.pop(left_tree[0])
                
                forest.remove(left_tree)
                
                pass
            
            else:
                # 两棵树相似性不同
                new_tree_node = TreeNode(info="inner", simi=pair[2], parent=None)
                
                new_tree_node.AddChild(tree1[0])
                new_tree_node.AddChild(tree2[0])
                
                new_tree_node.Depth = max(tree1[0].Depth, tree2[0].Depth) + 1
                tree1[0].Setparent(new_tree_node)
                tree2[0].Setparent(new_tree_node)
                
                new_nodes = tree1[1].union(tree2[1])
                
                forest.remove(tree1)
                forest.remove(tree2)
                forest.append((new_tree_node,new_nodes,))
                self.__leaves_info[new_tree_node] = tuple(new_nodes)
                pass
            
        if len(forest) is 1:
            print('this is a binary tree')
            return forest[0][0]
        else:
            # 不联通的情况
            new_tree_node = TreeNode(info="inner",simi=0.0, parent=None)
            new_nodes = set()
            depth_max = 0
            for node in forest:
                new_tree_node.AddChild(node[0])
                node[0].Setparent(new_tree_node)
                depth_max = max(depth_max,node[0].Depth)
                new_nodes.update(node[1])
            new_tree_node.Depth = depth_max + 1
            self.__leaves_info[new_tree_node] = tuple(new_nodes)
            return new_tree_node


    def __serialize(self, tree):
        if len(tree.children) is 0:
            return {'name': '%s'%tree.info, 'children': []}
        else:
            children = []
            for child in tree.children:
                children.append(self.__serialize(child))
            return {'name': '%s'%tree.info, 'children': children}
        
    def Serialize(self, tree=None):
        return self.__serialize(tree=self.__root)
    
    def GenerateCommunity(self, cut_simi_thr=0.0, least_com_num=0):
        subtrees =  DendrogramGenerator.__CutTree(self.__root,cut_simi_thr)
        community_list = [] # 在该划分结果下的社团
        for tree in subtrees:
            # 每一个社团
            one_com= self.__leaves_info[tree]
            if len(one_com) >= least_com_num:
                community_list.append(tuple(one_com))
        return community_list
    
    @classmethod
    def ConvertE2N(cls, edge_coms):
        node_coms = []
        for com in edge_coms:
            com_node_set = set()
            for edge in com:
                com_node_set.update(edge.node())
            node_coms.append(tuple(com_node_set))
        return node_coms

    @property
    def MaxDepth(self):
        return self.__root.Depth    
    
    @property
    def RootNode(self):
        return self.__root


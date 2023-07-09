from DPMConformanceExtension import ptml
from DPMConformanceExtension.obj import Operator
import math


def get_num_nodes(cur_node, f_l, layer):
    layer += 1
    cur_node._set_layer(layer)
    flag_loop = f_l
    if cur_node.operator is None:
        num_nodes = 1
        numofTransitions[cur_node.uid] = num_nodes
    elif cur_node.operator == Operator.XOR:
        num_nodes = 0
        for child in cur_node.children:
            num_nodes += get_num_nodes(child, flag_loop, layer)
        numofTransitions[cur_node.uid] = num_nodes
        xor_score[cur_node.uid] = num_nodes*(len(cur_node.children)-1)/len(cur_node.children)
        if flag_loop == 1:
            xor_score[cur_node.uid] = 0
    else:
        if cur_node.operator == Operator.LOOP:
            flag_loop = 1
        num_nodes = 0
        for child in cur_node.children:
            num_nodes += get_num_nodes(child, flag_loop, layer)
        numofTransitions[cur_node.uid] = num_nodes

    return num_nodes


def traverse_pt(cur_node):
    if cur_node.operator is not None:
        for child in cur_node.children:
            print(child.uid, " : ", child.priority)
            traverse_pt(child)
    else:
        print(cur_node.uid, " : ", cur_node.priority)


def set_node_priority(score, p, nodes, percent):

    max_layer = 0
    s=0
    for key, value in score.items():
        if value != 0:
            s+=1
    d_xor_num = percent
    i = 0
    xor_to_d = dict()
    for treenode in sorted(score.items(), key=lambda x: x[1], reverse=True):
        if treenode[1] != 0:
            nodes[treenode[0]]._set_priority(p)
            p += 1
        if i < d_xor_num:
            if nodes[treenode[0]].layer not in xor_to_d.keys():
                if nodes[treenode[0]].layer > max_layer:
                    max_layer = nodes[treenode[0]].layer
                xor_to_d[nodes[treenode[0]].layer] = dict()
                xor_to_d[nodes[treenode[0]].layer][treenode[0]] = 0
            else:
                xor_to_d[nodes[treenode[0]].layer][treenode[0]] = 0
            i += 1

    return nodes, xor_to_d, max_layer, d_xor_num


def get_priority_of_pt(pt, nodes, per):

    if pt.operator == Operator.LOOP:
        num = get_num_nodes(pt, 0, 0)
    else:
        num = get_num_nodes(pt, 0, 0)
    new_nodes, num_xor, max_layer, d_xor_n = set_node_priority(xor_score, 1, nodes, per)
    return new_nodes, num_xor, max_layer, d_xor_n


global xor_score 
xor_score = dict()
global numofTransitions 
numofTransitions = dict()

def clear_v():
    global numofTransitions
    numofTransitions = dict()
    global xor_score
    xor_score = dict()

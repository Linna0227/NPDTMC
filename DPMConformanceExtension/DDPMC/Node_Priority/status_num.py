import ptml
from obj import Operator
import math
def get_num_nodes(cur_node, f_l, up, re, re_xor_list, layer):
    re = []
    re_xor_list = []



    flag_loop = f_l

    under_parallel = up
    num_nodes = 0
    c_score = 0
    branches = 1
    states_for_cur = 0
    Transition_of_max_branch[cur_node.uid] = 0
    layer += 1
    cur_node._set_layer(layer)
    if cur_node.operator is None:
        if under_parallel == 1:
            re.append(cur_node.uid)
        num_nodes = 1
        numofTransitions[cur_node.uid] = num_nodes
        states[cur_node.uid] = num_nodes
        Transition_of_max_branch[cur_node.uid] = 1
        return num_nodes, re, re_xor_list
    elif cur_node.operator == Operator.XOR:
        max_num = 0

        for child in cur_node.children:
            child_num_nodes, child_re, child_re_xor = get_num_nodes(child, flag_loop, under_parallel, [],[], layer)
            num_nodes += child_num_nodes
            re += child_re
            re_xor_list += child_re_xor
            states_for_cur += states[child.uid]
            if Transition_of_max_branch[child.uid] > max_num:
                max_num = Transition_of_max_branch[child.uid]
        Transition_of_max_branch[cur_node.uid] = max_num
        if under_parallel == 1:
            re_xor_list.append(cur_node)
            re.append(cur_node.uid)
        for child in cur_node.children:
            c_score += (states_for_cur-states[child.uid])

        numofTransitions[cur_node.uid] = num_nodes
        states[cur_node.uid] = states_for_cur
        xor_score[cur_node.uid] = c_score/(len(cur_node.children))
        if flag_loop == 1:
            xor_score[cur_node.uid] = 0
        return num_nodes, re, re_xor_list
    elif cur_node.operator == Operator.SEQUENCE:
        if under_parallel == 1:
            re.append(cur_node.uid)
        for child in cur_node.children:
            child_num_nodes, child_re, child_re_xor = get_num_nodes(child, flag_loop, under_parallel, [], [], layer)
            num_nodes += child_num_nodes
            re += child_re
            re_xor_list += child_re_xor
            states_for_cur += states[child.uid]
            Transition_of_max_branch[cur_node.uid] += Transition_of_max_branch[child.uid]

        states[cur_node.uid] = states_for_cur
        return num_nodes, re, re_xor_list
    elif cur_node.operator == Operator.PARALLEL:
        if under_parallel == 1:
            re.append(cur_node.uid)
        under_parallel = 1
        re_compute_list = dict()
        re_xor_score_list = dict()
        for child in cur_node.children:
            child_num_nodes, child_re, child_re_xor = get_num_nodes(child, flag_loop, under_parallel, [], [], layer)
            num_nodes += child_num_nodes
            re_xor_list += child_re_xor
            re += child_re
            re_compute_list[child] = child_re
            re_xor_score_list[child] = child_re_xor
            Transition_of_max_branch[cur_node.uid] += Transition_of_max_branch[child.uid]
        for child in cur_node.children:
            states_for_cur += states[child.uid]*(Transition_of_max_branch[cur_node.uid]-Transition_of_max_branch[child.uid])
        states[cur_node.uid] = states_for_cur

        for re_node, re_node_child in re_compute_list.items():
            for re_child in re_node_child:
                states[re_child] = states[re_child]*(Transition_of_max_branch[cur_node.uid]-Transition_of_max_branch[re_node.uid])
        for cur_child, re_xor in re_xor_score_list.items():
            for xor in re_xor:
                if xor_score[xor.uid] != 0:
                    r_c_score = 0
                    for xor_child in xor.children:
                        r_c_score += (states[xor.uid] - states[xor_child.uid])
                    xor_score[xor.uid] = r_c_score / (len(xor.children))


        return num_nodes, re, re_xor_list
    elif cur_node.operator == Operator.LOOP:
        if under_parallel == 1:
            re.append(cur_node.uid)
        flag_loop = 1
        for child in cur_node.children:
            child_num_nodes, child_re, child_re_xor = get_num_nodes(child, flag_loop, under_parallel, [], [], layer)
            states_for_cur += states[child.uid]
            re_xor_list += child_re_xor

            num_nodes += child_num_nodes
            re += child_re
        Transition_of_max_branch[cur_node.uid] += Transition_of_max_branch[cur_node.children[0].uid]
        states[cur_node.uid] = states_for_cur
        numofTransitions[cur_node.uid] = num_nodes
        return num_nodes, re, re_xor_list
    else:
        print("Error!")



def traverse_pt(cur_node):
    if cur_node.operator is not None:
        for child in cur_node.children:
            print(child.uid, " : ", child.priority)
            traverse_pt(child)
    else:
        print(cur_node.uid, " : ", cur_node.priority)


def set_node_priority(score, p, nodes, percent):
    max_layer = 0
    
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



global numofTransitions
global states
global xor_score
global num_of_branches
global Transition_of_max_branch

numofTransitions = dict()
states = dict()
xor_score = dict()
num_of_branches = dict()
Transition_of_max_branch = dict()
def clear_v():
    global numofTransitions
    global states
    global xor_score
    global num_of_branches
    global Transition_of_max_branch
    numofTransitions = dict()
    states = dict()
    xor_score = dict()
    num_of_branches = dict()
    Transition_of_max_branch = dict()

def get_priority_of_pt(pt, nodes, per):

    if pt.operator == Operator.LOOP:
        num, rr, rx = get_num_nodes(pt, 1, 0, [], [], 0)
    else:
        num, rr, rx = get_num_nodes(pt, 0, 0, [], [], 0)
    new_nodes, num_xor, max_layer, d_xor_n = set_node_priority(xor_score, 1, nodes, per)
    return new_nodes, num_xor, max_layer, d_xor_n

from obj import Operator
from copy import deepcopy
import itertools


def set_current_child(tr, index, node):
    node.children[index] = tr
    tr._set_parent(node)


def merge(node, list_trees):
    for comb_trees in list_trees:
        for tr, index in comb_trees.items():
            set_current_child(tr, index[1], node)

def decompose_tree(current_tree, node_map, current_node, xor_d, current_layer, lowest_priority):
    subtrees_list = dict()
    while current_layer > 1:
        while len(xor_d[current_layer]) != 0:
            tree_node, tree_node_value = xor_d[current_layer].popitem()
            if tree_node_value == 0:

                    current_tree = node_map[tree_node]
                    parent_node = current_tree.parent
                    parent_layer = current_layer - 1
                    for child in parent_node.children:
                        xor_d[current_layer][child.uid] = 1
                        if child.uid not in subtrees_list.keys():
                            if child.operator == Operator.XOR and child.priority <= lowest_priority:
                                if child.uid not in subtrees_list.keys():
                                    current_child_list = list()
                                    for child_tree in child.children:
                                        decom_tree = deepcopy(child_tree)
                                        decom_tree.parent = None
                                        current_child_list.append(decom_tree)
                                    subtrees_list[child.uid] = current_child_list

                            else:
                                temp = list()
                                decom_tree = deepcopy(child)
                                decom_tree.parent = None
                                temp.append(decom_tree)
                                if child.uid not in subtrees_list.keys():
                                    subtrees_list[child.uid] = temp
                    child_list = list()

                    if parent_node.operator == Operator.XOR and parent_node.priority <= lowest_priority:
                        for child in parent_node.children:
                            for sub_tree in subtrees_list[child.uid]:
                                child_list.append(sub_tree)
                        subtrees_list[parent_node.uid] = child_list
                    else:
                        for child in parent_node.children:
                            child_list.append(subtrees_list[child.uid])
                        new_comb = itertools.product(*child_list)
                        current_tree_list = list()
                        for comb in new_comb:
                            i = 0
                            for tree_node in comb:
                                parent_node.children[i] = tree_node
                                i += 1
                                tree_node._set_parent(parent_node)
                            new_subtree = deepcopy(parent_node)
                            new_subtree.parent = None
                            current_tree_list.append(new_subtree)
                        subtrees_list[parent_node.uid] = current_tree_list
                    if parent_layer in xor_d.keys():
                        if parent_node not in xor_d[parent_layer].keys():
                            xor_d[parent_layer][parent_node.uid] = 0
                    else:
                        xor_d[parent_layer] = {parent_node.uid: 0}
        current_layer -= 1

    return subtrees_list












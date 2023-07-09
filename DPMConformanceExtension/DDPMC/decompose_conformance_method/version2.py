from traceback import print_tb
import Node_Priority
import trace_allocate
import conformance_algorithm
from pm4py.objects.log.obj import EventLog, Trace, Event
from decompose_conformance_method import decomposetree2
import time
import pm4py
import to_petri_net as pt_converter
from obj import Operator

import pm4py.algo.conformance.alignments.petri_net.algorithm as at
from enum import Enum


class NodePriorityVariants(Enum):
    VERSION_ACTIVITY_NUN = Node_Priority.activity_num
    VERSION_STATUS_NUM = Node_Priority.status_num


class TraceAllocateVariants(Enum):
    VERSION_ACTIVITY_SET = trace_allocate.activity_set
    VERSION_TAR_SET = trace_allocate.tar_set
    VERSION_ACTIVITY_SET_IMPROVE = trace_allocate.activity_set_improve
    VERSION_RANDOM_SELECTION = trace_allocate.random_selection


class ConformanceVariants(Enum):
    VERSION_ALIGNMENT = conformance_algorithm.call_for_alignment
    VERSION_TOKEN_REPLAY = conformance_algorithm.call_for_token


DEFAULT_NodePriorityVARIANT = Node_Priority.activity_num
DEFAULT_TraceAllocateVARIANT = TraceAllocateVariants.VERSION_ACTIVITY_SET
DEFAULT_ConformanceVARIANT = ConformanceVariants.VERSION_ALIGNMENT


def get_method(method):
    if isinstance(method, Enum):
        return method.value
    return method


def compute_cost(node):
    if node.operator is None:
        if node.label is not None:
            return 10000
        else:
            return 1
    else:
        if node.operator == Operator.SEQUENCE or node.operator == Operator.PARALLEL:
            cost =0
            for child in node.children:
                cost += compute_cost(child)
        if node.operator == Operator.XOR:
            m = compute_cost(node.children[0])
            for child in node.children[1:]:
                n = compute_cost(child)
                if n < m:
                    m = n
            cost = m
        if node.operator == Operator.LOOP:
            child = node.children[0]
            cost = compute_cost(child)

    return cost


def get_tree_cost(tree):
    root = tree._get_root()
    current_node = root
    tree_cost = compute_cost(current_node)
    return tree_cost


def decom_conformance(eventlog, pt, tree_nodes_dict, decom_percent, conformance_algorithm=DEFAULT_ConformanceVARIANT, priority_method=DEFAULT_NodePriorityVARIANT, trace_allocate_method=DEFAULT_TraceAllocateVARIANT):

    new_nodes, xor_to_d, max_layer, d_xor_num = get_method(priority_method).get_priority_of_pt(pt, tree_nodes_dict, decom_percent)
    root = pt._get_root()
    d_s_time = time.clock()
    nodes_trees_list = decomposetree2.decompose_tree(pt, new_nodes, root, xor_to_d, max_layer, d_xor_num)
    d_e_time = time.clock()
    print("Time to decompose the model :", d_e_time-d_s_time)

    sub_trees_list = nodes_trees_list[root.uid]
    trees = list()

    for subtree in sub_trees_list:
        subtree.parent = None
        

        net, im, fm = pt_converter.apply(subtree)
        trees.append([(net, im, fm), subtree])

    current_log_confor_result = []
    for trace in eventlog:

        most_suitable_model = get_method(trace_allocate_method).get_model(trace, trees)
        log=EventLog()
        log.append(trace)
        trace_confor_result = get_method(conformance_algorithm).apply(log, most_suitable_model[0], most_suitable_model[1], most_suitable_model[2])
        trace_confor_result[0]['bwc'] = len(trace)
        current_log_confor_result.append(trace_confor_result[0])
    return current_log_confor_result


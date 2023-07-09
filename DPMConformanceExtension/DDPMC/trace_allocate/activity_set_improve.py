import pm4py
import ptml
from pm4py.util import xes_constants as xes
import pm4py
from pm4py.objects.log.obj import Trace, Event
from pm4py.util import constants as pm4_constants
from obj import Operator


def get_subtree_activity_set(pt):
    if len(pt.act_set) == 0:
        if pt.operator is not None:
            current_tree_act_set = set()
            for c_tree in pt.children:
                act_for_child = get_subtree_activity_set(c_tree)
                current_tree_act_set = current_tree_act_set.union(act_for_child)
            pt._set_act_set(current_tree_act_set)
        else:
            c_set = set()
            c_set.add(pt.label)
            pt._set_act_set(c_set)
    return pt.act_set


def get_shortest_path(node):
    path = set()
    if node.operator is None:
        if node.label is not None:
            path.add(node.label)
        return path
    else:
        if node.operator == Operator.SEQUENCE or node.operator == Operator.PARALLEL:
            for child in node.children:
                c_path = get_shortest_path(child)
                path = path.union(c_path)

        if node.operator == Operator.XOR:
            path = get_shortest_path(node.children[0])
            c_opt_path_num = len(path)
            for child in node.children:
                if child.operator is None and child.label is None:
                    return path
                else:
                    c_path = get_shortest_path(child)
                    c_path_num = len(c_path)
                    if c_path_num < c_opt_path_num:
                        c_opt_path_num = c_path_num
                        path = c_path
        if node.operator == Operator.LOOP:
            child = node.children[0]
            path = get_shortest_path(child)

    return path


def reduce_tree_to_trace_size_activity(trace, process_tree):
    trace_fragments = list()
    sub_tree_act_list = list()
    if process_tree.operator is not None:
        for i in range(len(process_tree.children)):
            cur_act = get_subtree_activity_set(process_tree.children[i])
            sub_tree_act_list.append(cur_act)
            trace_fragments.append(list())
    else:
        sub_tree_act_list.append(get_subtree_activity_set(process_tree))
        trace_fragments.append(list())
    j = 0
    i = 0
    while i < len(trace):
        if trace[i] in sub_tree_act_list[j]:
            trace_fragments[j].append(trace[i])
            i = i+1
        else:
            j += 1
            if j == len(sub_tree_act_list):
                j = 0
    missing_acts = set()
    reduced_acts = set()
    if process_tree.operator == Operator.SEQUENCE or process_tree.operator == Operator.PARALLEL:

        for i in range(len(trace_fragments)):
            if len(trace_fragments[i]) == 0:
                c_missing_activities = get_shortest_path(process_tree.children[i])
                reduced_activities = set()
            else:
                c_missing_activities, reduced_activities = reduce_tree_to_trace_size_activity(trace_fragments[i], process_tree.children[i])
            missing_acts = missing_acts.union(c_missing_activities)
            reduced_acts = reduced_acts.union(reduced_activities)

    elif process_tree.operator == Operator.XOR:
        branches_dev = list()
        branches_missing_list = list()
        act_num = 0
        branches_reduced_acts = list()
        for frag in trace_fragments:
            act_num += len(set(frag))
            branches_dev.append(0)
            branches_missing_list.append(set())
            branches_reduced_acts.append(set())
        for i in range(len(trace_fragments)):
            if len(trace_fragments[i]) == 0:
                c_missing_activities = get_shortest_path(process_tree.children[i])
                branches_dev[i] = len(c_missing_activities) + act_num-len(trace_fragments[i])
                branches_missing_list[i] = c_missing_activities
                branches_reduced_acts[i] = set()
            else:
                c_missing_activities, reduced_activities = reduce_tree_to_trace_size_activity(trace_fragments[i],
                                                                                              process_tree.children[i])
                branches_dev[i] = len(c_missing_activities) + act_num - len(reduced_activities)
                branches_missing_list[i] = c_missing_activities
                branches_reduced_acts[i] = reduced_activities
        c_dev = branches_dev[0]
        missing_acts = branches_missing_list[0]
        reduced_acts = branches_reduced_acts[0]
        for i in range(len(branches_dev)):
            if branches_dev[i] <= c_dev:
                c_dev = branches_dev[i]
                missing_acts = branches_missing_list[i]
                reduced_acts = branches_reduced_acts[i]
    elif process_tree.operator == Operator.LOOP:
        if len(trace_fragments[0]) == 0:
            missing_acts = get_shortest_path(process_tree.children[0])
            reduced_acts = set()
        else:
            if len(trace_fragments[1]) == 0:
                missing_acts, reduced_acts = reduce_tree_to_trace_size_activity(trace_fragments[0],
                                                                                              process_tree.children[0])
            else:
                for i in range(len(trace_fragments)):
                    c_missing_activities, reduced_activities = reduce_tree_to_trace_size_activity(trace_fragments[i],
                                                                                                  process_tree.children[
                                                                                                      i])
                    missing_acts = missing_acts.union(c_missing_activities)
                    reduced_acts = reduced_acts.union(reduced_activities)
    else:
        if len(trace_fragments[0]) >= 1:
            reduced_acts.add(process_tree.label)
        else:
            missing_acts.add(process_tree.label)
    return missing_acts, reduced_acts


def get_trace_set(trace_a):
    parameters = {}
    activity_key = parameters[
        pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    trace_activities = [event[activity_key] for event in trace_a]
    trace_set = set(trace_activities)
    # print(trace_set)
    return trace_set


def get_model_score(m_set, t_set):
    inter_for_mt = m_set.intersection(t_set)
    dev = len(m_set-inter_for_mt)+len(t_set-inter_for_mt)
    return dev


def get_model(o_trace, sub_nets):
    trace_act_set = get_trace_set(o_trace)
    current_score = 100000000000000000000
    m_net = sub_nets
    current_net = m_net[0][0]
    for one_net in m_net:
        model_act_set = get_subtree_activity_set(one_net[1])
        c_trace = list()
        parameters = {}
        activity_key = parameters[
            pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
        for event in o_trace:
            if event[activity_key] in model_act_set:
                c_trace.append(event[activity_key])

        if len(c_trace) == 0:
            model_score = len(o_trace)+len(get_shortest_path(one_net[1]))
        else:
            missing_act_set, reduced_act_set = reduce_tree_to_trace_size_activity(c_trace, one_net[1])

            model_set = missing_act_set.union(reduced_act_set)

            model_score = get_model_score(model_set, trace_act_set)

        if model_score <= current_score:
            current_score = model_score
            current_net = one_net[0]
    return current_net

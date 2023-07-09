from pm4py.util import constants as pm4_constants
from pm4py.util import xes_constants as xes


def get_treeleaves(ptree):
    if len(ptree.act_set) == 0:

        leaves = list()
        if ptree._get_children() != list():
            child_nodes = ptree._get_children()
            getleaves = True
            while getleaves:
                leaves_to_replace = list()
                new_childnodes = list()
                for child in child_nodes:
                    if child._get_children() != list():
                        leaves_to_replace.append(child)
                    else:
                        leaves.append(child.label)
                if leaves_to_replace != list():
                    for child in leaves_to_replace:
                        for el in child.children:
                            new_childnodes.append(el)
                    child_nodes = new_childnodes
                else:
                    getleaves = False
        else:
            leaves.append(ptree.label)
        ptree._set_act_set(set(leaves))
    return ptree.act_set



def get_trace_set(trace_a):

    parameters = {}
    activity_key = parameters[
        pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    trace_activities = [event[activity_key] for event in trace_a]
    trace_set = set(trace_activities)
    return trace_set


def get_model_score(set1, set2):
    a = set1.intersection(set2)
    b = set1.union(set2)
    if len(a) > 0:
        score = len(a)/len(b)
    else:
        score = 0
    return score


def get_model(o_trace, sub_nets):
    trace_act_set = get_trace_set(o_trace)
    current_score = 0
    m_net = sub_nets
    current_net = m_net[0][0]
    for one_net in m_net:
        model_act_set = get_treeleaves(one_net[1])
        model_score = get_model_score(model_act_set, trace_act_set)
        if model_score >= current_score:
            current_score = model_score
            current_net = one_net[0]
    return current_net





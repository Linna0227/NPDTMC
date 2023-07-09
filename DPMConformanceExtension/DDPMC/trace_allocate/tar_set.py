import pm4py
from pm4py.visualization.process_tree import visualizer as pt_visualizer
import getTAR
from pm4py.util import constants as pm4_constants
from pm4py.util import xes_constants as xes

def get_trace_tar(trace, ak):
    trace_tar_set = set()
    if len(trace) == 0:
        trace_tar_set.add('start_node->end_node')
    elif len(trace) == 1:
        trace_tar_set.add('start_node' + '->' + trace[0][ak])
        trace_tar_set.add(trace[0][ak] + '->' + 'end_node')
    else:
        for i in range(len(trace)):
            if i == 0:
                print(trace[0][ak])
                trace_tar_set.add('start_node' + '->' + trace[0][ak])
            else:
                r = trace[i-1][ak] + "->" + trace[i][ak]
                trace_tar_set.add(r)
        trace_tar_set.add(trace[len(trace)-1][ak] + '->' + 'end_node')
    return trace_tar_set


def get_model_score(model_tar_set, trace_act_set):
    a = model_tar_set.intersection(trace_act_set)
    if len(trace_act_set) >0:
        score = len(a)/len(trace_act_set)
    else:
        score = 0
    return score


def get_model(o_trace, sub_nets):
    parameters = {}
    activity_key = parameters[
            pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    trace_tar_set = get_trace_tar(o_trace,activity_key)

    current_score = 0
    m_net = sub_nets
    current_net = m_net[0][0]
    for one_net in m_net:
        model_tar_set = getTAR.get_PT_TARSet(one_net[1])
        model_score = get_model_score(model_tar_set, trace_tar_set)
        if model_score >= current_score:
            current_score = model_score
            current_net = one_net[0]
    return current_net


from locale import currency
# import ptml
import time
import openpyxl as op
import time
import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.util import xes_constants as xes
from pm4py.util import constants as pm4_constants
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pyspark import SparkContext
import time
import sys
# from pm4py.objects.conversion.wf_net import converter as wf_net_converter
from pm4py.util import exec_utils
from pm4py.statistics.variants.log import get as variants_module
from pm4py.algo.conformance.alignments.petri_net.algorithm import Parameters
# import hrdecomposetreela as dt
from copy import copy
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY, PARAMETER_CONSTANT_CASEID_KEY


# covert rdd strings to log 
def covertToXlog(traces):
    log=EventLog()
    parameters={}
    activity_key = parameters[
        pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    for traceString in traces:
        # traceString=re.sub(r'[0-9]+,', '', traceString)
        traceString=traceString.strip('\n')
        eventnames=traceString.split(",")
        if len(eventnames) >1:
            trace=Trace()
            trace._set_attributes({'concept:name': eventnames[0]})
            if eventnames[1:] == ['']:
                log.append(trace)
            else:
                for name in eventnames[1:]:
                    event=Event()
                    event[activity_key]=name
                    trace.append(event)
                log.append(trace)
            

    return log

# call function reformat times: number of partition blocks  (2 times)
def reformat(partitiondata):
    updatedata=list()
    updatedata.append(covertToXlog(partitiondata))
    return iter(updatedata)


def get_variants_structure(log, parameters):
    if parameters is None:
        parameters = copy({PARAMETER_CONSTANT_ACTIVITY_KEY: DEFAULT_NAME_KEY})

    parameters = copy(parameters)
    variants_idxs = exec_utils.get_param_value(Parameters.VARIANTS_IDX, parameters, None)
    if variants_idxs is None:
        variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)

    one_tr_per_var = []
    variants_list = []
    for index_variant, var in enumerate(variants_idxs):
        variants_list.append(var)

    for var in variants_list:
        one_tr_per_var.append(log[variants_idxs[var][0]])

    return variants_idxs, one_tr_per_var


def form_result(log, variants_idxs, all_result):
    al_idx = {}
    for index_variant, variant in enumerate(variants_idxs):
        for trace_idx in variants_idxs[variant]:
            al_idx[trace_idx] = all_result[index_variant]

    results_con = []
    for i in range(len(log)):
        results_con.append(al_idx[i])

    return results_con


def cost_alignment(partitiondatas):
    m_net=broadcast_net.value
    aligned_traces=list()
    for ilog in partitiondatas:
        variants_id,variant_traces=get_variants_structure(ilog,None)
        # print(variant_traces)
        aligned_ilog=list()
        for one_trace in variant_traces:
            cur_cost = 100000000000000000000000
            eve_r = dict()
            for net in m_net:
            # confer_net = get_method(trace_allocate_method).get_model(one_trace, m_net)
                log=EventLog()
                log.append(one_trace)
                aligned_trace=alignments.apply_log(log,net[0],net[1],net[2])
                if aligned_trace[0]['cost'] < cur_cost:
                    aligned_trace[0]['bwc']=len(one_trace)
                    cur_cost = aligned_trace[0]['cost']
                    eve_r = aligned_trace[0]

            aligned_ilog.append(eve_r)
        r_f_ilog=form_result(ilog,variants_id,aligned_ilog)
        aligned_traces.append(r_f_ilog)
    return iter(aligned_traces)

if __name__=="__main__":
    sc = SparkContext( )
    tree_p = sys.argv[1]
    log_path = sys.argv[2]
    numofnet = sys.argv[3]
    partition_n = sys.argv[4]

    numofnet=int(numofnet)
    partition_n=int( partition_n)
    model_path = "/home/hadoop/Projects/submodels/"
    s = time.time()
       
    submodels = list()
    for i in range(numofnet):
        sm = pm4py.read_pnml(model_path+tree_p+"/"+str(i)+".pnml")
        submodels.append(sm)


    sc.addPyFile("/home/hadoop/Projects/DDPMC.zip")
    broadcast_net=sc.broadcast(submodels)
    l_start_time=time.time()  
    log = sc.textFile(log_path,partition_n)
    sublogs=log.mapPartitions(reformat)
    d_result = sublogs.mapPartitions(cost_alignment).collect()
    e = time.time()
    cost = 0
    for r in d_result:
        for dr in r:
            if dr["cost"] >=10000:
                print(dr)
            cost+=dr["cost"]//10000
    
    print("---------------------------------------------------")
    print("---------------------------------------------------")
    print("---------------------------------------------------")
    print("Program runtime:",e-s)
    print("cost for alignment:",cost)
    print("---------------------------------------------------")
    print("---------------------------------------------------")
    print("---------------------------------------------------")

    sc.stop()



    










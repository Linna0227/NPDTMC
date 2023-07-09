from fileinput import filename
from pm4py.algo.conformance.alignments.decomposed import algorithm
from pm4py.algo.conformance.alignments.decomposed.variants.recompos_maximal import get_best_worst_cost
import pm4py
import time
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.util import xes_constants as xes
from pm4py.util import constants as pm4_constants
def evaluate(aligned_traces, best_worse_model_cost):
    # no_traces = len([x for x in aligned_traces if x is not None])
    no_traces = 0
    no_fit_traces = 0
    sum_fitness = 0.0
    sum_bwc = 0.0
    sum_cost = 0.0
    # queued_states = 0
    # traversed_arcs = 0

    tr_align = []

    i=0
    un = 0

    for tr in aligned_traces:
        if tr is not None:
            no_traces += 1
            # print(tr)
            if tr["fitness"] == 1.0:
                no_fit_traces = no_fit_traces + 1
            # sum_fitness += tr["fitness"]
            sum_bwc = sum_bwc + len(log[i]) + best_worse_model_cost
            sum_cost += tr["cost"]//10000
            
            sum_fitness += tr["fitness"]

            tr_align.append(tr)
        else:
            un+=1 
        i+=1

    perc_fit_traces = 0.0
    average_fitness = 0.0
    log_fitness = 0.0
    print("number of unreliable result",un)
    print("no_fit_traces",no_fit_traces)
    print("no_traces",no_traces)

    if no_traces > 0:
        perc_fit_traces = (100.0 * float(no_fit_traces)) / (float(no_traces))
        average_fitness = float(sum_fitness) / float(no_traces)
        log_fitness = 1.0 - float(sum_cost) / float(sum_bwc)
    print("sum_cost:", sum_cost)
    print("sum_bwc:", sum_bwc)
    return tr_align, {"percFitTraces": perc_fit_traces, "averageFitness": average_fitness,
                      "log_fitness": log_fitness}





log_path="/home/hadoop/Projects/testdata/data/L1/L1.xes"
net_path="/home/hadoop/Projects/testdata/data/L1/L1.pnml"
net,im,fm = pm4py.read_petri_net(net_path)
# print(net.transitions)
log = pm4py.read_xes(log_path)

s= time.time()

from pm4py.algo.conformance.alignments.decomposed import algorithm as decomp_alignments
res = decomp_alignments.apply(log, net, im, fm)
e = time.time()
cost = get_best_worst_cost(net,im,fm)
log_res = evaluate(res,cost)
print("Program runtime:",e-s)
print("fitness",log_res[1])

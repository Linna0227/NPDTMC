from pm4py.algo.conformance.alignments.process_tree.variants.approximated import original
import pm4py
from pm4py.objects.process_tree.utils.generic import process_tree_to_binary_process_tree
import time
from pm4py.objects.process_tree.obj import Operator
from pm4py.algo.conformance.alignments.process_tree.variants.approximated import matrix_lp


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
                # print(child, ",", cost)
        if node.operator == Operator.XOR:
            m = compute_cost(node.children[0])
            # print("m", m)
            for child in node.children[1:]:
                n = compute_cost(child)
                # print("n", n)
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
            sum_cost += tr["cost"]
            

            # queued_states += tr['queued_states']
            # traversed_arcs += tr['traversed_arcs']

            # tr["bwc"]=tr["bwc"]+best_worse_model_cost
            # print(tr["bwc"]+best_worse_model_cost)
            # if float(len(log[i]) + best_worse_model_cost) >0:
            #     tr["fitness"] = 1 - float(tr["cost"]) / float((len(log[i]) + best_worse_model_cost)) 
            # else:
            #     tr["fitness"] = 0
            sum_fitness += tr["fitness"]

            tr_align.append(tr)
        else:
            un+=1
            # print("unreliable")
            # print(log[i])
            
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

log_path="/home/hadoop/Projects/testdata/data/BPM2013/newlog/new_prEm6.xes"
tree_path="/home/hadoop/Projects/testdata/data/BPM2013/Multitree/prEm6.ptml"
tree = pm4py.read_ptml(tree_path)
log = pm4py.read_xes(log_path)
b_tree = process_tree_to_binary_process_tree(tree)
s= time.time()
res = matrix_lp.apply(log, b_tree)
e = time.time()
print("Program runtime:",e-s)
best_cost = get_tree_cost(tree)//10000
fitness = evaluate(res, best_cost)
print("fitness",fitness[1])
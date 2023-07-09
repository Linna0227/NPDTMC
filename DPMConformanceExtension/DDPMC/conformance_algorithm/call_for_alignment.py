from pm4py.algo.conformance.alignments.petri_net import algorithm


def apply(trace, petri_net, initial_marking, final_marking):
    result = algorithm.apply_log(trace, petri_net, initial_marking, final_marking)
    return result



def evaluate(aligned_traces, best_worse_model_cost):
    # no_traces = len([x for x in aligned_traces if x is not None])
    no_traces = 0
    no_fit_traces = 0
    sum_fitness = 0.0
    sum_bwc = 0.0
    sum_cost = 0.0
    queued_states = 0
    traversed_arcs = 0

    tr_align = []

    for block in aligned_traces:
        # print(block)
        for tr in block:
            if tr is not None:
                no_traces += 1
                # print(tr)
                if tr["fitness"] == 1.0:
                    no_fit_traces = no_fit_traces + 1
                sum_bwc = sum_bwc + tr["bwc"] + best_worse_model_cost
                sum_cost += tr["cost"]//10000

                queued_states += tr['queued_states']
                traversed_arcs += tr['traversed_arcs']
                if float((tr["bwc"] + best_worse_model_cost)) >0:
                    tr["fitness"] = 1 - float(tr["cost"]//10000) / float((tr["bwc"] + best_worse_model_cost)) 
                else:
                    tr["fitness"] = 0
                sum_fitness += tr["fitness"]

                tr_align.append(tr)

    perc_fit_traces = 0.0
    average_fitness = 0.0
    log_fitness = 0.0
    print("no_fit_traces",no_fit_traces)
    print("no_traces",no_traces)

    if no_traces > 0:
        perc_fit_traces = (100.0 * float(no_fit_traces)) / (float(no_traces))
        average_fitness = float(sum_fitness) / float(no_traces)
        log_fitness = 1.0 - float(sum_cost) / float(sum_bwc)
    print("sum_cost:", sum_cost)
    print("sum_bwc:", sum_bwc)
    return tr_align, {"percFitTraces": perc_fit_traces, "averageFitness": average_fitness,
                      "log_fitness": log_fitness, "queued_states": queued_states, "traversed_arcs": traversed_arcs}

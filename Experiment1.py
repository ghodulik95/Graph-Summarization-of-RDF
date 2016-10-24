from texting import sendMessage
from Uniform_Pure_Randomized_Summary import Uniform_Pure_Randomized_Summary
from Altered_Reduced_Cost_Summary import Altered_Reduced_Cost_Summary
import Graph_Importer
import logging
import os
from multiprocessing import Process,Pool


def run_experiment_1(num,appendage=""):
    if num <= 4:
        graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("wordnet")
        logging.basicConfig(filename="Wordnet.log",level=logging.INFO)
    else:
        graph, oid_to_uri, uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")
        logging.basicConfig(filename="DBLP4.log", level=logging.INFO)

    script_dir = os.path.dirname(__file__)
    terminate = 518400/2
    prefix = "Noooop"
    message = None
    try:

        if num == 1:
            prefix = os.path.join(script_dir,"Experiment1/UniformWordnetInclude1Degree"+appendage)

            summary = Uniform_Pure_Randomized_Summary(graph,oid_to_uri,uri_to_oid,
                                                      macro_filename=prefix+"Macro.txt",
                                                      merge_filename=prefix+"Merge.csv",
                                                      iterative_filename=prefix+"Iterative.csv",
                                                      iterative_logging_factor=1000,
                                                      early_terminate=terminate,
                                                      log_merges=True,
                                                      remove_one_degree=False,
                                                      correction_both_directions=False,
                                                      putEdges=False
                )
        if num == 2:
            prefix = os.path.join(script_dir,"Experiment1/UniformWordnetNotInclude1Degree"+appendage)
            summary = Uniform_Pure_Randomized_Summary(graph,oid_to_uri,uri_to_oid,
                                                      macro_filename=prefix+"Macro.txt",
                                                      merge_filename=prefix+"Merge.csv",
                                                      iterative_filename=prefix+"Iterative.csv",
                                                      iterative_logging_factor=1000,
                                                      early_terminate=terminate,
                                                      log_merges=True,
                                                      remove_one_degree=True,
                                                      correction_both_directions=False,
                                                      putEdges=False
                )
        if num == 3:
            prefix = os.path.join(script_dir,"Experiment1/AlteredWordnetNotInclude1Degree"+appendage)
            summary = Altered_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,
                                                      macro_filename=prefix+"Macro.txt",
                                                      merge_filename=prefix+"Merge.csv",
                                                      iterative_filename=prefix+"Iterative.csv",
                                                      iterative_logging_factor=10000,
                                                      early_terminate=terminate,
                                                      log_merges=True,
                                                      remove_one_degree=True,
                                                      correction_both_directions=False,
                                                      putEdges=False,
                                                      initial_rc_cutoff=0.5,
                                                      num_skips=100,
                                                      step=0.1,
                )
        if num == 4:
            prefix = os.path.join(script_dir,"Experiment1/AlteredWordnetInclude1Degree"+appendage)
            summary = Altered_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,
                                                      macro_filename=prefix+"Macro.txt",
                                                      merge_filename=prefix+"Merge.csv",
                                                      iterative_filename=prefix+"Iterative.csv",
                                                      iterative_logging_factor=10000,
                                                      early_terminate=terminate,
                                                      log_merges=True,
                                                      remove_one_degree=False,
                                                      correction_both_directions=False,
                                                      putEdges=False,
                                                      initial_rc_cutoff=0.5,
                                                      num_skips=100,
                                                      step=0.1
                )

        if num == 5:
            prefix = os.path.join(script_dir, "Experiment1/UniformDBLP4Include1Degree"+appendage)

            summary = Uniform_Pure_Randomized_Summary(graph, oid_to_uri, uri_to_oid,
                                                      macro_filename=prefix + "Macro.txt",
                                                      merge_filename=prefix + "Merge.csv",
                                                      iterative_filename=prefix + "Iterative.csv",
                                                      iterative_logging_factor=1000,
                                                      early_terminate=terminate,
                                                      log_merges=True,
                                                      remove_one_degree=False,
                                                      correction_both_directions=False,
                                                      putEdges=False
                                                      )
        if num == 6:
            prefix = os.path.join(script_dir, "Experiment1/UniformDBLP4NotInclude1Degree"+appendage)
            summary = Uniform_Pure_Randomized_Summary(graph, oid_to_uri, uri_to_oid,
                                                      macro_filename=prefix + "Macro.txt",
                                                      merge_filename=prefix + "Merge.csv",
                                                      iterative_filename=prefix + "Iterative.csv",
                                                      iterative_logging_factor=1000,
                                                      early_terminate=terminate,
                                                      log_merges=True,
                                                      remove_one_degree=True,
                                                      correction_both_directions=False,
                                                      putEdges=False
                                                      )
        if num == 7:
            prefix = os.path.join(script_dir, "Experiment1/AlteredDBLP4NotInclude1Degree"+appendage)
            summary = Altered_Reduced_Cost_Summary(graph, oid_to_uri, uri_to_oid,
                                                   macro_filename=prefix + "Macro.txt",
                                                   merge_filename=prefix + "Merge.csv",
                                                   iterative_filename=prefix + "Iterative.csv",
                                                   iterative_logging_factor=10000,
                                                   early_terminate=terminate,
                                                   log_merges=True,
                                                   remove_one_degree=True,
                                                   correction_both_directions=False,
                                                   putEdges=False,
                                                   initial_rc_cutoff=0.5,
                                                   num_skips=100,
                                                   step=0.1,
                                                   )
        if num == 8:
            prefix = os.path.join(script_dir, "Experiment1/AlteredDBLP4Include1Degree"+appendage)
            summary = Altered_Reduced_Cost_Summary(graph, oid_to_uri, uri_to_oid,
                                                   macro_filename=prefix + "Macro.txt",
                                                   merge_filename=prefix + "Merge.csv",
                                                   iterative_filename=prefix + "Iterative.csv",
                                                   iterative_logging_factor=10000,
                                                   early_terminate=terminate,
                                                   log_merges=True,
                                                   remove_one_degree=False,
                                                   correction_both_directions=False,
                                                   putEdges=False,
                                                   initial_rc_cutoff=0.5,
                                                   num_skips=100,
                                                   step=0.1
                                                   )
        if num == 9:
            prefix = os.path.join(script_dir, "Experiment1/UniformWordnetInclude1Degree" + appendage)

            summary = Uniform_Pure_Randomized_Summary(graph, oid_to_uri, uri_to_oid,
                                                      macro_filename=prefix + "Macro.txt",
                                                      merge_filename=prefix + "Merge.csv",
                                                      iterative_filename=prefix + "Iterative.csv",
                                                      iterative_logging_factor=1000,
                                                      early_terminate=terminate,
                                                      log_merges=True,
                                                      remove_one_degree=False,
                                                      correction_both_directions=False,
                                                      putEdges=False
                                                      )
    except Exception as e:
        message = prefix+" Failed: "#+e.message
        logging.error(message)
        sendMessage(message)

    if message is None:
        message = prefix+" Finished"
        logging.info(message)
        sendMessage(message)

def run_experiment1_custom():
    pass


if __name__ == '__main__':
    #p = Pool(processes=4)
    #p.map(run_experiment_1,range(5,9))
    run_experiment_1(1,"NoHighDegreeTest")

"""
for i in range(2):
    print i
    add = 4*i
    p1 = Process(target=run_experiment_1,args)
    p1.start()
    print("Yup")
    p2 = Process(target=run_experiment_1(1 + add))
    p2.start()
    print("Yup")
    p3 = Process(target=run_experiment_1(1 + add))
    p3.start()
    print("Yup")
    p4 = Process(target=run_experiment_1(1 + add))
    p4.start()
    print("Yup")

    sleep = (518400 / 2) + 3600
    #time.sleep(sleep)
"""
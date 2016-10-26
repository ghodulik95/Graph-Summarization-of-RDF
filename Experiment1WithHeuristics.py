from texting import sendMessage
from UniformRandomCustom import UniformRandomCustom
from AlteredReducedCostCustomSummary import AlteredReducedCostCustomSummary
import Graph_Importer
import Graph_Exporter
import logging
import os
from multiprocessing import Process, Pool
from NonUniformCustom import NonUniformRandomCustom
from GroupUniformRandomCustom import GroupUniformRandomCustom
from LocalGreedyCustom import LocalGreedyCustom
import itertools

dbnames = ["wordnet","IMDBSmall","DBLP4"]
algs = ["LocalGreedy" ]#"Group","NonUniform","Pure","Altered"]
remove_one_degree = [True]
merge_identical = [True]
# initial_rc_cutoff,num_allowable_skips,step
altered_params = (0.5, 100, 0.01)


def get_filename(param_tuple):
    ret = param_tuple[0] + param_tuple[1]
    if param_tuple[0] == 'Altered':
        ret += "_" + str(int(param_tuple[4] * 100)) + "_" + str(param_tuple[5]) + "_" + str(
            int(param_tuple[6] * 100))
    return ret


def get_early_terminate(param_tuple):
    return 0.9999
    """if not param_tuple[2] and param_tuple[3]:
        if param_tuple[0] == 'Pure':
            return 0.9999
        if param_tuple[0] == 'Altered' and param_tuple[4] == (0.5, 100, 0.1):
            return 0.9999
    return 0.4"""


def get_params():
    ret = []
    params = algs, dbnames, remove_one_degree, merge_identical
    for element in itertools.product(*params):
        if element[0] == 'Altered':
            element += altered_params
        ret.append(element)
    return ret


def record_termination(message, failure):
    if failure:
        logging.error(message)
    else:
        logging.info(message)
    sendMessage(message)


def log(message):
    print message
    logging.info(message)


params = get_params()


def run_an_experiment(num):
    param_tuple = params[num]
    filename_prefix = get_filename(param_tuple)
    try:

        early_terminate = get_early_terminate(param_tuple)
        make_summary = True

        filename_with_path = os.path.join(os.path.dirname(__file__), "Experiment1_Custom_Output_Heuristics/" + filename_prefix)
        logging.basicConfig(filename="Experiment1_Custom_Heuristics", level=logging.INFO)
        log(filename_prefix + " started")

        try:
            graph, oid_to_uri, uri_to_oid, = Graph_Importer.import_graph_regular(param_tuple[1], include_real_name=True,
                                                                                 fulldb=True)
        except Exception as e:
            record_termination(filename_prefix + " failed on graph import: " + str(e.message), True)
            return -1
        log(filename_prefix + " starting summarization")
        try:
            if param_tuple[0] == 'Altered':
                g = AlteredReducedCostCustomSummary(g=graph,
                                                    oid_to_uri=oid_to_uri,
                                                    uri_to_oid=uri_to_oid,
                                                    dbname=param_tuple[1],
                                                    macro_filename=filename_with_path + "Macro.txt",
                                                    merge_log_filename=filename_with_path + "Merge.csv",
                                                    iterative_log_filename=filename_with_path + "Iterative.csv",
                                                    log_factor=0.05,
                                                    initial_rc_cutoff=param_tuple[4],
                                                    num_allowable_skips=param_tuple[5],
                                                    step=param_tuple[6],
                                                    dbSerializationName=filename_prefix,
                                                    num_merges_to_log=0,
                                                    remove_one_degree=param_tuple[2],
                                                    merge_identical=param_tuple[3],
                                                    early_terminate=early_terminate,
                                                    make_summary=make_summary)
            elif param_tuple[0] == 'Pure':
                g = UniformRandomCustom(g=graph,
                                        oid_to_uri=oid_to_uri,
                                        uri_to_oid=uri_to_oid,
                                        dbname=param_tuple[1],
                                        macro_filename=filename_with_path + "Macro.txt",
                                        merge_log_filename=filename_with_path + "Merge.csv",
                                        iterative_log_filename=filename_with_path + "Iterative.csv",
                                        log_factor=0.05,
                                        dbSerializationName=filename_prefix,
                                        num_merges_to_log=0,
                                        remove_one_degree=param_tuple[2],
                                        merge_identical=param_tuple[3],
                                        early_terminate=early_terminate,
                                        make_summary=make_summary)
            elif param_tuple[0] == 'NonUniform':
                g =  NonUniformRandomCustom(g=graph,
                                            oid_to_uri=oid_to_uri,
                                            uri_to_oid=uri_to_oid,
                                            dbname=param_tuple[1],
                                            macro_filename=filename_with_path + "Macro.txt",
                                            merge_log_filename=filename_with_path + "Merge.csv",
                                            iterative_log_filename=filename_with_path + "Iterative.csv",
                                            log_factor=0.05,
                                            dbSerializationName=filename_prefix,
                                            num_merges_to_log=0,
                                            remove_one_degree=param_tuple[2],
                                            merge_identical=param_tuple[3],
                                            early_terminate=early_terminate,
                                        make_summary=make_summary)
            elif param_tuple[0] == 'Group':
                g = GroupUniformRandomCustom(g=graph,
                                           oid_to_uri=oid_to_uri,
                                           uri_to_oid=uri_to_oid,
                                           dbname=param_tuple[1],
                                           macro_filename=filename_with_path + "Macro.txt",
                                           merge_log_filename=filename_with_path + "Merge.csv",
                                           iterative_log_filename=filename_with_path + "Iterative.csv",
                                           log_factor=0.05,
                                           dbSerializationName=filename_prefix,
                                           num_merges_to_log=0,
                                           remove_one_degree=param_tuple[2],
                                           merge_identical=param_tuple[3],
                                           early_terminate=early_terminate,
                                           make_summary=make_summary)
            elif param_tuple[0] == 'LocalGreedy':
                g = LocalGreedyCustom(g=graph,
                                           oid_to_uri=oid_to_uri,
                                           uri_to_oid=uri_to_oid,
                                           dbname=param_tuple[1],
                                           macro_filename=filename_with_path + "Macro.txt",
                                           merge_log_filename=filename_with_path + "Merge.csv",
                                           iterative_log_filename=filename_with_path + "Iterative.csv",
                                           log_factor=0.05,
                                           dbSerializationName=filename_prefix,
                                           num_merges_to_log=0,
                                           remove_one_degree=param_tuple[2],
                                           merge_identical=param_tuple[3],
                                           early_terminate=25000,
                                           make_summary=make_summary)
        except Exception as e:
            record_termination(filename_prefix + " failed on summarization: " + str(e.message), True)
            return -2

        if early_terminate is None or True:
            log(filename_prefix + " starting export")
            try:
                Graph_Exporter.export_summary(g, param_tuple[1], filename_prefix)
            except Exception as e:
                record_termination(filename_prefix + " failed on export: " + e.message, True)
                return -3
            record_termination(filename_prefix + " finished successfully.", False)
            return 0
    except Exception as e:
        record_termination(filename_prefix + " failed somewhere else: " + str(e.message), True)
        return -4
    record_termination(filename_prefix + " finished", False)


def run_emperiment_1():
    print len(params)


if __name__ == '__main__':
    non_dblp = filter(lambda x: params[x][1] != 'DBLP4', range(len(params)))
    #non_dblp = non_dblp[3:]
    dblp = filter(lambda x: params[x][1] == 'DBLP4', range(len(params)))
    try:
        p = Pool(processes=2)
        p.map(run_an_experiment, non_dblp)

        p = Pool(processes=1)
        p.map(run_an_experiment, dblp)
    except Exception as e:
        record_termination("TOTAL FAILURE",True)
        record_termination(str(e.message),True)


def oldmain():
    logging.basicConfig(filename="Experiment1_CustomScore", level=logging.INFO)
    """
    record_termination("Starting",False)
    try:
        graph, oid_to_uri, uri_to_oid, = Graph_Importer.import_graph_regular("wordnet", include_real_name=True,
                                                                             fulldb=True)
        filename_prefix = "wordnetRandomScore"
        filename_with_path = os.path.join(os.path.dirname(__file__), "Experiment1_Custom_Output_Heuristics/" + filename_prefix)
        g = NonUniformRandomCustom(g=graph,
                                oid_to_uri=oid_to_uri,
                                uri_to_oid=uri_to_oid,
                                dbname="wordnet",
                                macro_filename=filename_with_path + "Macro.txt",
                                merge_log_filename=filename_with_path + "Merge.csv",
                                iterative_log_filename=filename_with_path + "Iterative.csv",
                                log_factor=0.02,
                                dbSerializationName=filename_prefix,
                                num_merges_to_log=350,
                                remove_one_degree=True,
                                merge_identical=True,
                                early_terminate=0.9999,
                                make_summary=True)
        Graph_Exporter.export_summary(g, "wordnet", filename_prefix)
    except Exception as e:
        record_termination("Failed at 1",True)
        record_termination(str(e.message),True)
    record_termination("Finished 1",False)

    try:
        graph, oid_to_uri, uri_to_oid, = Graph_Importer.import_graph_regular("wordnet", include_real_name=True,
                                                                             fulldb=True)
        filename_prefix = "wordnetRemove1MergeIdenticalUniform"
        filename_with_path = os.path.join(os.path.dirname(__file__),
                                          "Experiment1_Custom_Output_Heuristics/" + filename_prefix)
        g = WordnetScoredRandomUnvisited(g=graph,
                                         oid_to_uri=oid_to_uri,
                                         uri_to_oid=uri_to_oid,
                                         dbname="wordnet",
                                         macro_filename=filename_with_path + "Macro.txt",
                                         merge_log_filename=filename_with_path + "Merge.csv",
                                         iterative_log_filename=filename_with_path + "Iterative.csv",
                                         log_factor=0.02,
                                         dbSerializationName=filename_prefix,
                                         num_merges_to_log=350,
                                         remove_one_degree=True,
                                         merge_identical=True,
                                         early_terminate=0.9999,
                                         make_summary=True)
        Graph_Exporter.export_summary(g, "wordnet", filename_prefix)

    except Exception as e:
        record_termination("Failed at 2",True)
        record_termination(str(e.message),True)
    record_termination("Finished 2",False)

    try:
        graph, oid_to_uri, uri_to_oid, = Graph_Importer.import_graph_regular("wordnet", include_real_name=True,
                                                                             fulldb=True)
        filename_prefix = "wordnetRandomScore2"
        filename_with_path = os.path.join(os.path.dirname(__file__),
                                          "Experiment1_Custom_Output_Heuristics/" + filename_prefix)
        g = WordnetScoredRandomUnvisited(g=graph,
                                         oid_to_uri=oid_to_uri,
                                         uri_to_oid=uri_to_oid,
                                         dbname="wordnet",
                                         macro_filename=filename_with_path + "Macro.txt",
                                         merge_log_filename=filename_with_path + "Merge.csv",
                                         iterative_log_filename=filename_with_path + "Iterative.csv",
                                         log_factor=0.02,
                                         dbSerializationName=filename_prefix,
                                         num_merges_to_log=350,
                                         remove_one_degree=True,
                                         merge_identical=True,
                                         early_terminate=0.9999,
                                         make_summary=True)
        Graph_Exporter.export_summary(g, "wordnet", filename_prefix)

    except Exception as e:
        record_termination("Failed at 3", True)
        record_termination(str(e.message), True)
    record_termination("Finished 3", False)

    try:
        graph, oid_to_uri, uri_to_oid, = Graph_Importer.import_graph_regular("wordnet", include_real_name=True,
                                                                             fulldb=True)
        filename_prefix = "wordnetRemove1MergeIdenticalUniform2"
        filename_with_path = os.path.join(os.path.dirname(__file__),
                                          "Experiment1_Custom_Output_Heuristics/" + filename_prefix)
        g = WordnetScoredRandomUnvisited(g=graph,
                                         oid_to_uri=oid_to_uri,
                                         uri_to_oid=uri_to_oid,
                                         dbname="wordnet",
                                         macro_filename=filename_with_path + "Macro.txt",
                                         merge_log_filename=filename_with_path + "Merge.csv",
                                         iterative_log_filename=filename_with_path + "Iterative.csv",
                                         log_factor=0.02,
                                         dbSerializationName=filename_prefix,
                                         num_merges_to_log=350,
                                         remove_one_degree=True,
                                         merge_identical=True,
                                         early_terminate=0.9999,
                                         make_summary=True)
        Graph_Exporter.export_summary(g, "wordnet", filename_prefix)
    except Exception as e:
        record_termination("Failed at 4", True)
        record_termination(str(e.message), True)
    record_termination("Finished 4", False)
    """

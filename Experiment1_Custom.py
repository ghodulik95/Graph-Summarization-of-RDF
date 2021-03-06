from texting import sendMessage
from UniformRandomCustom import UniformRandomCustom
from AlteredReducedCostCustomSummary import AlteredReducedCostCustomSummary
import Graph_Importer
import Graph_Exporter
import logging
import os
from multiprocessing import Process,Pool
import itertools

dbnames = ["wordnet"]#["DBLP4","IMDBSmall","SP2B","LUBM","uniprot","wordnet"]
algs = ["Pure"]#["Pure","Altered"]
remove_one_degree = [True, False]
merge_identical = [True, False]
#initial_rc_cutoff,num_allowable_skips,step
altered_params = [(0.5,10,0.01),(0.5,100,0.1),
                  (0.45,10,0.01),(0.45,100,0.1)
                  ]
def get_filename(param_tuple):
    ret = param_tuple[0]+param_tuple[1]
    if param_tuple[2]:
        ret += "Remove1Degree"

    if param_tuple[3]:
        ret += "MergeIdentical"

    if param_tuple[0] == 'Altered':
        ret += "_"+str(int(param_tuple[4][0]*100))+"_"+str(param_tuple[4][1])+"_"+str(int(param_tuple[4][2]*100))
    return ret

def get_early_terminate(param_tuple):
    if not param_tuple[2] and param_tuple[3]:
        if param_tuple[0] == 'Pure':
            return 0.9999
        if param_tuple[0] == 'Altered' and param_tuple[4] == (0.5,100,0.1):
            return 0.9999
    return 0.4

def get_params():
    ret = []
    for alg in algs:
        params = [alg],dbnames,remove_one_degree,merge_identical
        for element in itertools.product(*params):
            if element[0] == 'Altered' and (element[2] or not element[3]):
                ret.append((element[0], element[1], element[2], element[3],(0.5,100,0.05)))
            elif element[0] == 'Altered':
                ret.append((element[0], element[1], element[2], element[3],(0.5,100,0.1)))
                ret.append((element[0], element[1], element[2], element[3],(0.5,10,0.01)))
                ret.append((element[0], element[1], element[2], element[3],(0.45,10,0.01)))
                ret.append((element[0], element[1], element[2], element[3],(0.45,100,0.1)))
            else:
                ret.append(element)
    return ret

def record_termination(message,failure):
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
        make_summary = early_terminate is None

        filename_with_path = os.path.join(os.path.dirname(__file__),"Experiment1_Custom_Output/"+filename_prefix)
        logging.basicConfig(filename="Experiment1_Custom",level=logging.INFO)
        log(filename_prefix+ " started")

        try:
            graph, oid_to_uri, uri_to_oid, = Graph_Importer.import_graph_regular(param_tuple[1], include_real_name=True, fulldb=True)
        except Exception as e:
            record_termination(filename_prefix+" failed on graph import: "+str(e.message),True)
            return -1
        log(filename_prefix + " starting summarization")
        try:
            if param_tuple[0] == 'Altered':
                g = AlteredReducedCostCustomSummary(g=graph,
                                                    oid_to_uri=oid_to_uri,
                                                    uri_to_oid=uri_to_oid,
                                                    dbname=param_tuple[1],
                                                    macro_filename=filename_with_path+"Macro.txt",
                                                    merge_log_filename=filename_with_path+"Merge.csv",
                                                    iterative_log_filename=filename_with_path+"Iterative.csv",
                                                    log_factor=0.05,
                                                    initial_rc_cutoff=param_tuple[4][0],
                                                    num_allowable_skips=param_tuple[4][1],
                                                    step=param_tuple[4][2],
                                                    dbSerializationName=filename_prefix,
                                                    num_merges_to_log=350,
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
                                        merge_log_filename=filename_with_path+"Merge.csv",
                                        iterative_log_filename=filename_with_path + "Iterative.csv",
                                        log_factor=0.05,
                                        dbSerializationName=filename_prefix,
                                        num_merges_to_log=350,
                                        remove_one_degree=param_tuple[2],
                                        merge_identical=param_tuple[3],
                                        early_terminate=early_terminate,
                                        make_summary=make_summary)
        except Exception as e:
            record_termination(filename_prefix+" failed on summarization: "+str(e.message),True)
            return -2

        if early_terminate is None:
            log(filename_prefix + " starting export")
            try:
                Graph_Exporter.export_summary(g,param_tuple[1],filename_prefix)
            except Exception as e:
                record_termination(filename_prefix+" failed on export: "+e.message,True)
                return -3
            record_termination(filename_prefix+" finished successfully.",False)
            return 0
    except Exception as e:
        record_termination(filename_prefix + " failed somewhere else: " + str(e.message), True)
        return -4
    record_termination(filename_prefix + " finished", False)
    
    

def run_emperiment_1():
    print len(params)

if __name__ == '__main__':
    #run_an_experiment(0)
    try:
        p = Pool(processes=1)
        p.map(run_an_experiment, range(0,len(params)-1))
    except Exception as e:
        record_termination("TOTAL FAILURE",True)
        record_termination(e.message,True)

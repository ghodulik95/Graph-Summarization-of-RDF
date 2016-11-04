from __future__ import print_function
import Query
import random
import time
import os
import cPickle
import itertools

dbnames = ["DBLP4", "LUBM", "wordnet", "IMDBSmall"]
algs = ["Pure","None","Altered","NonUniformSecondHerusitc"]

def get_params():
    ret = []
    for element in itertools.product(dbnames,algs):
        ret.append(element)
    return ret

def get_random_queries(dbname,num_seeds=5,depth=4):
    script_dir = os.path.dirname(__file__)
    serialization_filename = os.path.join(script_dir, "Serializations/"+ dbname + str(num_seeds) + "queries"+str(depth)+".p")
    if os.path.isfile(serialization_filename):
        deserial = cPickle.load(open(serialization_filename, "rb"))
        return deserial
    b = Query.BreadthQueryer(dbname)
    nodes = b.get_all_nodes()
    seeds = random.sample(nodes,num_seeds)
    queries = []
    for s in seeds:
        print("started seed")
        for i in range(1,depth):
            print("started hop %d" % i)
            ihop = b.get_random_neighborhood(s,i)
            if len(ihop) > 5:
                end_points = random.sample(ihop,4)
            else:
                end_points = ihop
            for e in end_points:
                queries.append((s,e,i))
    cPickle.dump(queries, open(serialization_filename, "wb"))
    return queries

def run_an_experiment(dbname,alg,queries,appendage):
    script_dir = os.path.dirname(__file__)
    prefix = os.path.join(script_dir, "Experiment3/"+ dbname+ alg + appendage)

    if alg == "None":
        q = Query.BreadthQueryer(dbname)
    else:
        q = Query.SummaryQueryer(dbname,alg)

    macro = open(prefix+"Macro.csv", "w")
    print(q.get_macro_headers(), file=macro)
    numQs = len(queries)
    currQNum = 1
    for query in queries:
        output = q.connection_query(query[0], query[1], query[2])
        mac = output
        mic = None
        if alg != 'None':
            mac = output[0]
            mic = output[1]
            micro = open(prefix+"Trial"+str(q.trial_num)+".csv", "w")
            print(q.get_micro_headers(),file=micro)
            micro.write(mic)
            micro.close()
        print(mac,file=macro)
        macro.flush()
        print("Completed Query Number %d out of %d" % (currQNum, numQs))
        currQNum += 1

if __name__ == '__main__':
    random.seed(time.time())
    num_seeds = 10
    depth = 5
    for p in get_params():
        qs = get_random_queries(p[0], num_seeds,depth=depth)
        run_an_experiment(p[0], p[1], qs, "Run1")
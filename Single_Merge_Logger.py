from __future__ import print_function
from Abstract_Merge_Logger import Abstract_Merge_Logger
from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer
from Graph_Summary import Abstract_Graph_Summary
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector
from Node_Profile import Node_Profile
import Graph_Importer
import numpy
import cPickle
import os.path

class Single_Merge_Logger(Abstract_Merge_Logger):
    def __init__(self,log_file,graph_summary,graph_serialname):
        """
        :type graph_summary: Abstract_Graph_Summary
        :param log_file:
        :param graph_summary:
        """
        self.file_name=log_file.name
        self.graph_serialname = graph_serialname
        self.metric_combinations = self.get_metric_combinations()
        self.uri_to_oid = graph_summary.uri_to_oid
        Abstract_Merge_Logger.__init__(self,log_file,graph_summary)
        self.suv_tools = Abstract_Reduced_Cost_Based_Node_Filterer(graph_summary)

    def get_csv_headers(self):
        headers = []
        headers.append("Identifier")
        headers.append("SEED NODE size")
        headers.append("MERGE NODE size")
        for mc in self.metric_combinations:
            for nodes in mc[1]:
                if nodes != -1:
                    for stat in mc[2]:
                        nodeName = "SEED NODE "
                        if nodes == 1:
                            nodeName = "MERGE NODE "
                        metric = mc[0]+" "
                        headers.append(nodeName+metric+stat)
                else:
                    headers.append(mc[0])
        headers.append("is_best,Reduced Cost")
        return headers



    def get_metric_combinations(self):
        return [('degrees', [0 ,1], ['max','min','avg','median','deviation']),
                ('num2hop', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('deg2hopRatio', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('articulation_proximity', [0, 1], ['min']),
                ('articulation_nearest', [0, 1], ['as-is']),
                ('clustering', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('authority', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('hub_score', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                #('eccentricity', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                #'closeness', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('shared',[-1])]

    def build_node_data(self):
        script_dir = os.path.dirname(__file__)
        serialization_filename = os.path.join(script_dir,"Serializations/"+self.graph_serialname+".p")
        if os.path.isfile(serialization_filename):
            deserial = cPickle.load(open(serialization_filename,"rb"))
            self.node_data = deserial['node_data']
            self.uri_to_oid = deserial['uri_to_oid']
            print("LOADED SERIAL")
        else:
            all_node_ids = range(0,self.graph_summary.g.vcount())
            print(self.graph_summary.g.vcount())
            print(self.file_name+" "+"start")
            self.node_data['degrees'] = [v.degree() for v in self.graph_summary.g.vs]
            print(self.file_name+" "+"degrees done")
            articulation_points = set(self.graph_summary.g.articulation_points())
            print(self.file_name+" "+"articulation points found")
            self.node_data['num2hop'] = []
            self.node_data['deg2hopRatio'] = []
            self.node_data['articulation_proximity'] = []
            self.node_data['articulation_nearest'] = []
            for v in all_node_ids:
                neighbors = set(self.graph_summary.g.neighbors(v))
                two_hop = self.graph_summary.exact_n_hop_original_neighbors_from_oid(v,2)
                self.node_data['num2hop'].append(len(two_hop))
                if self.node_data['degrees'][v] > 0:
                    self.node_data['deg2hopRatio'].append( float(self.node_data['num2hop'][v]) / self.node_data['degrees'][v])
                else:
                    self.node_data['deg2hopRatio'][v].append( -1)
                art_proximitiy, art_closest = self.find_distance_to_articulation(v,neighbors,two_hop,articulation_points)
                self.node_data['articulation_proximity'].append(art_proximitiy)
                self.node_data['articulation_nearest'].append(art_closest)
                #print(v)
            print(self.file_name+" "+"num2hop done")
            print(self.file_name+" "+"deg2hop ratio done")
            print(self.file_name+" "+"articulation done")
            self.node_data['clustering'] = self.graph_summary.g.transitivity_local_undirected()
            print(self.file_name+" "+"clustering done")
            self.node_data['authority'] = self.graph_summary.g.authority_score()
            print(self.file_name+" "+"Auth score done")
            self.node_data['hub_score'] = self.graph_summary.g.hub_score()
            print(self.file_name+" "+"hub score done")
            #self.node_data['eccentricity'] = self.graph_summary.g.eccentricity()
            #print("Eccentricity done")
            #self.node_data['closeness'] = self.graph_summary.g.closeness()
            #print("Closeness done")
            serial = {'node_data':self.node_data,'uri_to_oid':self.uri_to_oid}
            cPickle.dump(serial, open(serialization_filename,"wb"))
            print(self.file_name+" "+"All done")


    def get_snode_metric(self,contains,metric,stats):
        #print(self.node_data[metric])
        #print(self.node_data[metric][0])
        metrics = [self.node_data[metric][int(i)] for i in contains]
        to_return = {}
        if 'max' in stats:
            to_return['max'] = max(metrics)
        if 'min' in stats:
            to_return['min'] = min(metrics)
        if 'avg' in stats:
            to_return['avg'] = float(sum(metrics)) / len(metrics)
        if 'median' in stats:
            to_return['median'] = numpy.median(metrics)
        if 'deviation' in stats:
            to_return['deviation'] = numpy.std(metrics)
        if 'as-is' in stats:
            to_return['as-is'] = metrics[0]
        return to_return

    def find_distance_to_articulation(self,v,neighbors,two_hop,articulation_points):
        if v in articulation_points:
            return 0,v
        n_intersect = neighbors.intersection(articulation_points)
        if len(n_intersect) > 0:
            return 1,n_intersect.pop()
        two_intersect = two_hop.intersection(articulation_points)
        if len(two_intersect) > 0:
            return 2,two_intersect.pop()
        return -1, None

    def log_merge(self,u,nodes,identifier="",reduced_cost=None,u_contains=None,merge_contains=None,is_best=False):
        """
        :param u:
        :param snodes:
        :type: snodes: set
        :return:
        """
        #print(nodes)
        assert len(nodes) == 1



        merge_node = None
        for x in nodes:
            merge_node = x
        if u_contains is None and merge_contains is None:
            u_snode_obj = self.graph_summary.s.vs.find(u)
            u_contains = u_snode_obj['contains']
            merge_node_obj = self.graph_summary.s.vs.find(merge_node)
            merge_contains = merge_node_obj['contains']
        row = str(identifier)+","+str(len(u_contains))+","+str(len(merge_contains))+","
        for mc in self.metric_combinations:
            metric = mc[0]
            for nodes in mc[1]:
                if nodes > -1:
                    stats = None
                    if nodes == 0:
                        stats = self.get_snode_metric(u_contains,metric,mc[2])
                    elif nodes == 1:
                        stats =  self.get_snode_metric(merge_contains,metric,mc[2])
                    for stat in mc[2]:
                        row += str(stats[stat])+","
                elif nodes == -1:
                    seed_neighbors = self.graph_summary.exact_n_hop_original_neighbors_from_supernode_name(u,1)
                    #num_seed_neighbors = len(seed_neighbors)
                    merge_neighbors = self.graph_summary.exact_n_hop_original_neighbors_from_supernode_name(merge_node,1)
                    #num_merge_neighbors = len(merge_neighbors)
                    num_shared_neighbors = len(seed_neighbors.intersection(merge_neighbors))
                    num_total_neighbors = len(seed_neighbors.union(merge_neighbors))
                    row += str(float(num_shared_neighbors)/num_total_neighbors)+","
        if reduced_cost is None:
            reduced_cost=self.calc_SUV(u,merge_node)[0]
        row += str(is_best)+","+str(reduced_cost)
        print(row,file=self.log_file)
        self.log_file.flush()

    def calc_SUV(self,u,v):
        if isinstance(u,Node_Profile):
            return u.calc_SUV(v)
        else:
            return self.suv_tools.calc_SUV(u,v)

    def get_merge_candidates(self,u):
        if isinstance(u,Node_Profile):
            return u.get_two_hop_neighbors()
        else:
            return self.graph_summary.get_merge_candidates(u)

    def get_contains(self,node,uri_to_oid=None):
        if isinstance(node,Node_Profile):
            return set(map(lambda x: uri_to_oid[x], list(node.contains)))
        else:
            return node['contains']

    def log_state_sample(self,identifier,unvisited,numToTry=100):
        ns = Uniform_Random_Node_Selector()
        numTried = 0
        while numTried < numToTry and len(unvisited) > 0:
            seed = ns.select_node(unvisited)
            candidates = list(self.get_merge_candidates(seed))
            reduced_costs = {n:self.calc_SUV(seed,n)[0] for n in candidates}
            best = max(reduced_costs, key=lambda x: reduced_costs[x])
            for c in candidates:
                self.log_merge(seed,{best},
                               identifier=identifier,
                               reduced_cost=reduced_costs[c],
                               u_contains=self.get_contains(seed,self.uri_to_oid),
                               merge_contains=self.get_contains(c,self.uri_to_oid),
                               is_best= c == best)

            unvisited.remove(seed)
            numTried += 1




    def get_max_avg_min(self,nums):
        return min(nums),float(sum(nums))/len(nums),max(nums)

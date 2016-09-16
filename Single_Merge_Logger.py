from __future__ import print_function
from Abstract_Merge_Logger import Abstract_Merge_Logger
from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer
from Graph_Summary import Abstract_Graph_Summary
import numpy


class Single_Merge_Logger(Abstract_Merge_Logger):
    def __init__(self,log_file,graph_summary):
        """
        :type graph_summary: Abstract_Graph_Summary
        :param log_file:
        :param graph_summary:
        """
        self.metric_combinations = self.get_metric_combinations()
        Abstract_Merge_Logger.__init__(self,log_file,graph_summary)
        self.suv_tools = Abstract_Reduced_Cost_Based_Node_Filterer(graph_summary)
        self.node_data = {}
        self.build_node_data()

    def get_csv_headers(self):
        headers = []
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



    def get_metric_combinations(self):
        return [('degrees', [0 ,1], ['max','min','avg','median','deviation']),
                ('num2hop', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('deg2hopRatio', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('articulation_proximity', [0, 1], ['min']),
                ('articulation_nearest', [0, 1], ['as-is']),
                ('clustering', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('authority', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('hub_score', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('eccentricity', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('closeness', [0, 1], ['max', 'min', 'avg', 'median', 'deviation']),
                ('shared',[-1])]

    def build_node_data(self):
        all_node_ids = range(0,self.graph_summary.g.vcount())
        self.node_data['degrees'] = [v.degree() for v in self.graph_summary.g.vs]
        self.node_data['num2hop'] = [len(self.graph_summary.exact_n_hop_original_neighbors_from_oid(v.index,2)) for v in self.graph_summary.g.vs ]
        self.node_data['deg2hopRatio'] = [float(self.node_data['num2hop'][i]) / self.node_data['degrees'][i] for i in all_node_ids]
        articulation_points = set(self.graph_summary.g.articulation_points())
        articulation_proximities = [self.find_distance_to_articulation(i,articulation_points) for i in all_node_ids]
        self.node_data['articulation_proximity'] = [a[1] for a in articulation_proximities]
        self.node_data['articulation_nearest'] = [a[0] for a in articulation_proximities]
        self.node_data['clustering'] = self.graph_summary.g.transitivity_local_undirected(vertices=all_node_ids)
        self.node_data['authority'] = self.graph_summary.g.authority_score()
        self.node_data['hub_score'] = self.graph_summary.g.hub_score()
        self.node_data['eccentricity'] = self.graph_summary.g.eccentricity(vertices=all_node_ids)
        self.node_data['closeness'] = self.graph_summary.g.closeness(vertices=all_node_ids)

    def get_snode_metric(self,contains,metric,stats):
        metrics = [self.node_data[metric][i] for i in contains]
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

    def find_distance_to_articulation(self,index,points):
        q = [(index,0)]
        seen = set()
        while(len(q) > 0):
            current,distance = q.pop()
            if current in points:
                return (current,distance)
            seen.add(current)
            neighbors = self.graph_summary.g.neighbors(current)
            for n in neighbors:
                if n not in seen:
                    q.insert(0,(n,distance + 1))
        return (None,-1)


    def log_merge(self,u,nodes):
        """
        :param u:
        :param snodes:
        :type: snodes: set
        :return:
        """

        assert len(nodes) == 1
        merge_node = None
        for x in nodes:
            merge_node = x
        u_snode_obj = self.graph_summary.s.vs.find(u)
        merge_node_obj = self.graph_summary.s.vs.find(merge_node)
        new_contains = u_snode_obj['contains'].union(merge_node_obj['contains'])

        seed_neighbors = self.graph_summary.exact_n_hop_original_neighbors_from_supernode_name(u,1)
        num_seed_neighbors = len(seed_neighbors)
        merge_neighbors = self.graph_summary.exact_n_hop_original_neighbors_from_supernode_name(merge_node,1)
        num_merge_neighbors = len(merge_neighbors)
        num_shared_neighbors = len(seed_neighbors.union(merge_neighbors))
        num_not_shared = num_seed_neighbors + num_merge_neighbors - num_shared_neighbors

        num_seed_2hop = len(self.graph_summary.exact_n_hop_original_neighbors_from_supernode_name(u,2))
        num_merge_2hop = len(self.graph_summary.exact_n_hop_original_neighbors_from_supernode_name(merge_node,2))

        suv = self.suv_tools.calc_SUV(u,merge_node)
        centralities_seed = self.graph_summary.g.betweenness(vertices=u_snode_obj['contains'],directed=False)
        centralities_seed_min,centralities_seed_avg,centralities_seed_max = self.get_max_avg_min(centralities_seed)
        centralities_merge = self.graph_summary.g.betweenness(vertices=merge_node_obj['contains'], directed=False)
        centralities_merge_min, centralities_merge_avg, centralities_merge_max = self.get_max_avg_min(centralities_merge)
        line = ','.join([u,merge_node,str(new_contains),str(num_seed_neighbors),str(num_seed_2hop),str(num_merge_neighbors),str(num_merge_2hop),str(num_shared_neighbors),str(num_not_shared),str(centralities_seed_min),str(centralities_seed_avg),str(centralities_seed_max),str(centralities_merge_min),str(centralities_merge_avg),str(centralities_merge_max),str(suv)])
        print(line,file=self.log_file)

    def get_max_avg_min(self,nums):
        return min(nums),float(sum(nums))/len(nums),max(nums)

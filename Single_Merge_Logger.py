from __future__ import print_function
from Abstract_Merge_Logger import Abstract_Merge_Logger
from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer

class Single_Merge_Logger(Abstract_Merge_Logger):
    def __init__(self,log_file,graph_summary):
        Abstract_Merge_Logger.__init__(self,log_file,graph_summary)
        self.suv_tools = Abstract_Reduced_Cost_Based_Node_Filterer(graph_summary)
        self.build_node_data()

    def get_csv_headers(self):
        return ["Seed Node","Merge Node","NewContains","NumSeedNeighbors","NumSeed2HopNeighbors","NumMergeNeighbors","NumMerge2HopNeighbors","NumSharedNeighbors","NumNotSharedNeighbors","MinCentralitySeed","AvgCentralitySeed","MaxCentralitySeed","MinCentralityMerge","AvgCentralityMerge","MaxCentralityMerge","Reduced Cost"]

    #def build_node_data(self):


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

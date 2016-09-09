from Abstract_Summary_Preprocessor import Abstract_Summary_Preprocessor
from Graph_Summary import Abstract_Graph_Summary

class Merge_Identical_Nodes_Preprocessor(Abstract_Summary_Preprocessor):
    def __init__(self,graph_summary):
        """
        :param graph_summary:
        :type graph_summary: Abstract_Graph_Summary
        """
        Abstract_Summary_Preprocessor.__init__(self,graph_summary)
        self.neighbors_to_nodes = {}

    def pre_process(self):
        self.populate_neighbors_map()
        nodes_to_merge = self.neighbors_to_nodes.values()
        self.merge_nodes(nodes_to_merge)

    def merge_nodes(self,nodes_to_merge):
        ordered_nodes_to_merge = sorted(list(nodes_to_merge),key=lambda x: -len(x))
        for to_merge in ordered_nodes_to_merge:
            self.graph_summary.merge_snodes_given_supernode_names(to_merge)

    def populate_neighbors_map(self):
        for v_name in self.graph_summary.s.vs['name']:
            v_neighbors = self.graph_summary.exact_n_hop_neighbors(v_name,1,remove_seed=True)
            v_neighbors_tuple = tuple(sorted(v_neighbors))
            if not self.neighbors_to_nodes.has_key(v_neighbors_tuple):
                self.neighbors_to_nodes[v_neighbors_tuple] = []
            self.neighbors_to_nodes[v_neighbors_tuple].append(v_name)


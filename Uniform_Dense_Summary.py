from Graph_Summary import Abstract_Graph_Summary
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector
from Dense_Subgraphs_Filterer import Dense_Subgraphs_Filterer

class Uniform_Dense_Summary(Abstract_Graph_Summary):
    def __init__(self,graph,oid_to_uri,uri_to_oid,macro_filename,micro_filename,**kwargs):
        Abstract_Graph_Summary.__init__(self,graph,oid_to_uri,uri_to_oid,macro_filename,micro_filename,**kwargs)

    def on_before_summarization(self):
        self.node_selector = Uniform_Random_Node_Selector()
        self.node_filterer = Dense_Subgraphs_Filterer(self.g)

    def merge_snodes(self, oids):
        return self.merge_snodes_given_oids(oids)

    def get_merge_candidates(self, oid):
        return self.exact_n_hop_original_neighbors_from_oid(oid,2)

    def generate_original_unvisited(self):
        return set([i for i in range(self.g.vcount())])
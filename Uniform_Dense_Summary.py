from Graph_Summary import Abstract_Graph_Summary
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector
from Dense_Subgraphs_Filterer import Dense_Subgraphs_Filterer

class Uniform_Dense_Summary(Abstract_Graph_Summary):
    def __init__(self,graph,oid_to_uri,uri_to_oid,macro_filename,micro_filename):
        Abstract_Graph_Summary.__init__(self,graph,oid_to_uri,uri_to_oid,macro_filename,micro_filename)

    def on_before_summarization(self):
        self.node_selector = Uniform_Random_Node_Selector()
        self.node_filterer = Dense_Subgraphs_Filterer(self.g)

    def merge_snodes(self, oids):
        self.s.add_vertices(1)
        new_index = self.s.vcount() - 1
        new_name = self.get_supernode_name(self.max_id)
        self.s.vs[new_index]['contains'] = oids
        self.s.vs[new_index]['name'] = new_name
        self.max_id += 1
        original_names = [self.oid_to_sname[i] for i in oids]
        current_ids = [self.s.vs.find(name) for name in original_names]
        for oid in oids:
            self.oid_to_sname[oid] = new_name
        self.s.delete_vertices(current_ids)
        return new_name


    def get_merge_candidates(self, oid):
        return self.exact_n_hop_original_neighbors_from_oid(oid,2)

    def generate_original_unvisited(self):
        return set([i for i in range(self.g.vcount())])
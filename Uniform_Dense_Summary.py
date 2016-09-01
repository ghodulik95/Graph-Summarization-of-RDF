from Graph_Summary import Abstract_Graph_Summary
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector
from Dense_Subgraphs_Filterer import Dense_Subgraphs_Filterer

class Uniform_Dense_Summary(Abstract_Graph_Summary):
    def __init__(self,graph,oid_to_uri,uri_to_oid,logger_filename):
        Abstract_Graph_Summary.__init__(self,graph,oid_to_uri,uri_to_oid,logger_filename)
        self.node_selector = Uniform_Random_Node_Selector()
        self.node_filterer = Dense_Subgraphs_Filterer(self.g)

        self.summarize()

    def node_select(self, s):
        return self.node_selector.select_node(s)

    def merge_supernodes(self, oids):
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

    def filter_merge_candidates(self,supernode,merge_candidates):
        return self.node_filterer.filter_nodes(supernode,merge_candidates)

    def generate_original_unvisited(self):
        return set([i for i in range(self.g.vcount())])
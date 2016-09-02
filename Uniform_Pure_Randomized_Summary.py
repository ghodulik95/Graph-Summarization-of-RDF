from Graph_Summary import Abstract_Graph_Summary
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector
from Pure_Randomized_Node_Filterer import Pure_Randomized_Node_Fileterer
import numpy.random as nprand

class Uniform_Pure_Randomized_Summary(Abstract_Graph_Summary):
    def __init__(self,graph,oid_to_uri,uri_to_oid,macro_filename,micro_filename):
        """
        :type graph: ig.Graph
        :type oid_to_uri: Dictionary
        :type uri_to_oid: Dictionary
        """
        Abstract_Graph_Summary.__init__(self,graph,oid_to_uri,uri_to_oid,macro_filename,micro_filename)

    def on_before_summarization(self):
        self.node_selector = Uniform_Random_Node_Selector()
        self.node_filterer = Pure_Randomized_Node_Fileterer(self)

    def merge_supernodes(self,snodes):
        assert len(snodes) == 2
        return Abstract_Graph_Summary.merge_supernodes(self,snodes)

    def get_merge_candidates(self,supernode_name):
        return self.exact_n_hop_neighbors(supernode_name,2)

    def update_unvisited(self,unvisited,to_merge,merged_name):
        """
        :param unvisited:
        :param to_merge:
        :param merged_name:
        :type unvisited: Set
        :type to_merge: Set
        :type merged_name: String
        :return:
        """
        Abstract_Graph_Summary.update_unvisited(self,unvisited,to_merge,merged_name)
        if merged_name is not None:
            unvisited.add(merged_name)


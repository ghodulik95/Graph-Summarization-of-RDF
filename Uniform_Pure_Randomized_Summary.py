from Graph_Summary import Abstract_Graph_Summary
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector
from Pure_Randomized_Node_Filterer import Pure_Randomized_Node_Fileterer
from Single_Merge_Logger import Single_Merge_Logger
from Merge_Identical_Nodes_Preprocessor import Merge_Identical_Nodes_Preprocessor
import numpy.random as nprand

class Uniform_Pure_Randomized_Summary(Abstract_Graph_Summary):
    def __init__(self, graph, oid_to_uri, uri_to_oid, macro_filename, merge_filename, **kwargs):
        """
        :type graph: ig.Graph
        :type oid_to_uri: Dictionary
        :type uri_to_oid: Dictionary
        """
        Abstract_Graph_Summary.__init__(self, graph, oid_to_uri, uri_to_oid, macro_filename, merge_filename, log_merges=True, **kwargs)

    def on_before_summarization(self):
        self.node_selector = Uniform_Random_Node_Selector()
        self.node_filterer = Pure_Randomized_Node_Fileterer(self)
        self.merge_logger = Single_Merge_Logger(self.micro, self)
        #preprocessor = Merge_Identical_Nodes_Preprocessor(self)
        #preprocessor.pre_process()

    def merge_supernodes(self,snodes,u):
        assert len(snodes) == 2
        return Abstract_Graph_Summary.merge_supernodes(self,snodes,u)

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


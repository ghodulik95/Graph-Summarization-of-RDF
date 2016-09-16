from Graph_Summary import Abstract_Graph_Summary
from Altered_Reduced_Cost_Node_Filterer import Altered_Reduced_Cost_Node_Filterer
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector
from Single_Merge_Logger import Single_Merge_Logger
from Merge_Identical_Nodes_Preprocessor import Merge_Identical_Nodes_Preprocessor

class Altered_Reduced_Cost_Summary(Abstract_Graph_Summary):
    def __init__(self, graph, oid_to_uri, uri_to_oid, macro_filename, merge_filename, **kwargs):
        Abstract_Graph_Summary.__init__(self, graph, oid_to_uri, uri_to_oid, macro_filename, merge_filename, log_merges=True, **kwargs)

    def expected_arguments(self):
        return {"initial_rc_cutoff","num_skips","step"}

    def on_before_summarization(self,initial_rc_cutoff,num_skips,step):
        self.node_selector = Uniform_Random_Node_Selector()
        self.node_filterer = Altered_Reduced_Cost_Node_Filterer(self,initial_rc_cutoff,num_skips,step)
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
        if len(to_merge) > 1 or self.node_filterer.zero_cutoff:
            Abstract_Graph_Summary.update_unvisited(self,unvisited,to_merge,merged_name)
            if merged_name is not None:
                unvisited.add(merged_name)


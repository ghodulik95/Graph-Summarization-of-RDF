from Graph_Summary import Abstract_Graph_Summary
from Group_Reduced_Cost_Node_Filterer import Single_Sweep_Group_Reduced_Cost_Node_Filterer
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector
from igraph import Graph
from Single_Merge_Logger import Single_Merge_Logger
from Merge_Identical_Nodes_Preprocessor import Merge_Identical_Nodes_Preprocessor


class Single_Sweep_Group_Reduced_Cost_Summary(Abstract_Graph_Summary):
    def __init__(self, graph, oid_to_uri, uri_to_oid, macro_filename, micro_filename, **kwargs):
        """
        :type graph: Graph
        :param graph:
        :param oid_to_uri:
        :param uri_to_oid:
        :param macro_filename:
        :param micro_filename:
        :param kwargs:
        """
        self.already_merged = set()
        self.max_merge_num = 0
        Abstract_Graph_Summary.__init__(self, graph, oid_to_uri, uri_to_oid, macro_filename, micro_filename,log_merges=False, **kwargs)

    def on_before_summarization(self):
        self.node_selector = Uniform_Random_Node_Selector()
        self.node_filterer = Single_Sweep_Group_Reduced_Cost_Node_Filterer(self)
        #self.merge_logger = Single_Merge_Logger(self.micro, self)
        #preprocessor = Merge_Identical_Nodes_Preprocessor(self)
        #preprocessor.pre_process()

    def merge_supernodes(self,snodes,u):
        new_name = Abstract_Graph_Summary.merge_supernodes(self,snodes,u)
        for n in self.s.vs.find(new_name)['contains']:
            self.g.vs[n]['iteration'] = self.max_merge_num
        self.max_merge_num += 1
        return new_name

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
        #to_merge.difference_update(self.already_merged)
        if len(to_merge) > 1 or self.node_filterer.zero_cutoff:
            Abstract_Graph_Summary.update_unvisited(self,unvisited,to_merge,merged_name)
        if merged_name is not None:
            unvisited.add(merged_name)
        #self.already_merged.update(to_merge)


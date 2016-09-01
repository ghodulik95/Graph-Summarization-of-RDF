from Graph_Summary import Abstract_Graph_Summary
import numpy.random as nprand

class Abstract_Non_Uniform_Randomized_Summary(Abstract_Graph_Summary):
    def __init__(self,graph,oid_to_uri,uri_to_oid,logger_filename):
        """
        :type graph: ig.Graph
        :type oid_to_uri: Dictionary
        :type uri_to_oid: Dictionary
        """
        Abstract_Graph_Summary.__init__(graph,oid_to_uri,uri_to_oid,logger_filename)
        self.original_prob_vector = self.generate_original_prob_vector()
        self.summarize()
        self.summary_finished =True

    def merge_supernodes(self,snodes):
        raise NotImplementedError()

    def filter_merge_candidates(self,supernode,merge_candidates):
        raise NotImplementedError()

    def update_unvisted(self,unvisited,merged):
        raise NotImplementedError()

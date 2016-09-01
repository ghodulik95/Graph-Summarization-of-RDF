from Abstract_Node_Selector import Abstract_Node_Selector
import numpy.random as nprand

class Abstrat_Non_Uniform_Node_Selector(Abstract_Node_Selector):
    def __init__(self,original_graph):
        Abstract_Node_Selector.__init__()
        self.original_prob_vector = self.generate_original_prob_vector(original_graph)

    def generate_original_prob_vector(self,original_graph):
        raise NotImplementedError()

    def generate_prob_vector(self,supernode_names):
        raise NotImplementedError()

    def node_select(self,s):
        slist = list(s)
        prob_vector = self.generate_prob_vector(slist)
        return nprand.choice(slist,p=prob_vector)
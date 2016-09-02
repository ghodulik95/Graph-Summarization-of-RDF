from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer

class Altered_Reduced_Cost_Node_Filterer(Abstract_Reduced_Cost_Based_Node_Filterer):
    def __init__(self,graph_summary, initial_rc_cutoff,num_skips,step):
        Abstract_Reduced_Cost_Based_Node_Filterer.__init__(self,graph_summary)

    def filter_nodes(self,supernode_name,candidate_names):
        pass
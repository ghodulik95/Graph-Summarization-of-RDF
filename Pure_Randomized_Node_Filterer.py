from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer

class Pure_Randomized_Node_Fileterer(Abstract_Reduced_Cost_Based_Node_Filterer):
    def __init__(self,graph_summary):
        """
        :param graph_summary:
        :type graph_summary: Abstract_Graph_Summary
        """
        Abstract_Reduced_Cost_Based_Node_Filterer.__init__(self,graph_summary)

    def filter_nodes(self,supernode_name,candidate_names):
        best_merge = None
        best_cost_reduction = 0
        suv_best = 0

        for name in candidate_names:
            suv,cost_reduction = self.calc_SUV(supernode_name,name)
            if suv > suv_best:
                best_merge = name
                suv_best = suv
                best_cost_reduction = cost_reduction

        self.cost_reduction += best_cost_reduction

        if best_merge is None:
            return set()
        else:
            return {best_merge}
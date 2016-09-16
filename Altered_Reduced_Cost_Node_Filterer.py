from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer

class Altered_Reduced_Cost_Node_Filterer(Abstract_Reduced_Cost_Based_Node_Filterer):
    def __init__(self,graph_summary, initial_rc_cutoff,num_skips,step):
        Abstract_Reduced_Cost_Based_Node_Filterer.__init__(self,graph_summary)

        self.initial_rc_cutoff = initial_rc_cutoff
        self.num_allowable_skips = num_skips
        self.step = step
        self.cur_skips = 0
        self.cur_cutoff = initial_rc_cutoff
        self.num_iterations = 0
        self.zero_cutoff = initial_rc_cutoff == 0

    def filter_nodes(self,supernode_name,candidate_names):
        best_merge = None
        suv_best = 0
        best_cost_reduction = 0
        for name in candidate_names:
            suv,cost_reduction = self.calc_SUV(supernode_name,name)
            if suv > suv_best:
                best_merge = name
                suv_best = suv
                best_cost_reduction =cost_reduction
        self.cost_reduction += best_cost_reduction
        self.num_iterations += 1
        if best_merge is None or ( not self.zero_cutoff and suv_best < self.cur_cutoff):
            self.cur_skips += 1
            if self.cur_skips > self.num_allowable_skips:
                self.cur_cutoff -= self.step
                if self.cur_cutoff < 0:
                    self.cur_cutoff = 0
                    self.zero_cutoff = True
                self.cur_skips = 0
            return set()
        else:
            return {best_merge}
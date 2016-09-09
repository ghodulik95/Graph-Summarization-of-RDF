from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer
from Abstract_Reduced_Cost_Based_Node_Filterer import Node_Profile

class Single_Sweep_Group_Reduced_Cost_Node_Filterer(Abstract_Reduced_Cost_Based_Node_Filterer):

    def __init__(self,graph_summary,cutoff):
        Abstract_Reduced_Cost_Based_Node_Filterer.__init__(self,graph_summary)
        self.num_iterations = 0
        assert 0 <= cutoff and cutoff <= 1
        self.cutoff = cutoff

    def filter_nodes(self,supernode_name,candidate_names):
        assert supernode_name not in candidate_names
        merge_reduced_costs = {c_name:self.calc_SUV(supernode_name,c_name) for c_name in candidate_names}
        sorted_candidates = sorted((list(candidate_names)),key=lambda x: merge_reduced_costs[x])
        sorted_candidates = filter(lambda x: merge_reduced_costs[x] > 0, sorted_candidates)
        curr_snode_profile = Node_Profile(supernode_name,self.graph_summary)
        to_merge = set()

        while len(sorted_candidates) > 0:
            candidate = sorted_candidates.pop()
            candidate_profile = Node_Profile(candidate,self.graph_summary)
            suv = self.get_reduced_cost_from_profiles(curr_snode_profile,candidate_profile)
            if suv > 0:
                curr_snode_profile.merge_with(candidate_profile)
                to_merge.add(candidate)

        self.num_iterations += 1
        if self.num_iterations % 100 == 0:
            print self.num_iterations

        return to_merge


    def calc_SUV_from_num_dicts(self,actual,potential,sum_degrees):
        cost = 0
        for n in actual.keys():
            a = actual[n]
            p = potential[n]
            assert a <= p
            if p - a + 1 <= a:
                cost += p - a + 1
            else:
                cost += a
        return 1 - (float(cost) / sum_degrees)
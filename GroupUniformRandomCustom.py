from CustomGraph import AbstractCustomGraphSummary
from CustomGraph import Node_Name_Table as NNT
from CustomGraph import Node_Profile as NP
import random

class GroupUniformRandomCustom(AbstractCustomGraphSummary):
    def __init__(self,g,oid_to_uri,uri_to_oid,dbname,macro_filename,merge_log_filename,iterative_log_filename,log_factor):
        AbstractCustomGraphSummary.__init__(self,g,oid_to_uri,uri_to_oid,dbname,macro_filename,merge_log_filename,iterative_log_filename,log_factor)

    def generate_original_unvisited(self):
        return self.super_nodes.copy()

    def node_select(self, s):
        return random.sample(s,1)[0]

    def filter_merge_candidates(self, u, merge_candidates):
        assert u not in merge_candidates
        merge_reduced_costs = {mc:u.calc_SUV(mc) for mc in merge_candidates}
        sorted_candidates = sorted(filter(lambda x: merge_reduced_costs[x] > 0, list(merge_reduced_costs.keys())), key=lambda y: merge_reduced_costs[y])
        curr_snode = u
        merged = {u}
        first = True

        while len(sorted_candidates) > 0:
            candidate = sorted_candidates.pop()
            suv,cost_reduction = curr_snode.calc_SUV(candidate)
            if suv > 0:
                curr_snode = NP.merge(curr_snode,candidate,self.name_table)
                self.cost_reduction += cost_reduction
                merged.add(candidate)
            elif first:
                return (merged,None)
            else:
                break
            first = False
        return (merged,curr_snode)

    def merge_supernodes(self, to_merge,u):
        return to_merge[1]

    def update_unvisited(self, unvisited, to_merge, u, merged_node):
        """
        :type unvisited: set
        :param unvisited:
        :param to_merge:
        :param u:
        :param merged_node:
        :return:
        """
        to_merge = to_merge[0]
        unvisited.difference_update(to_merge)
        if merged_node is not None:
            self.super_nodes.difference_update(to_merge)
            unvisited.add(merged_node)
            self.super_nodes.add(merged_node)
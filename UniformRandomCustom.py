from CustomGraph import AbstractCustomGraphSummary
from CustomGraph import Node_Name_Table as NNT
from CustomGraph import Node_Profile as NP
import random

class UniformRandomCustom(AbstractCustomGraphSummary):
    def __init__(self,g,oid_to_uri,uri_to_oid,dbname,macro_filename,merge_log_filename,iterative_log_filename,log_factor,dbSerializationName,num_merges_to_log,remove_one_degree=False,merge_identical=False):
        AbstractCustomGraphSummary.__init__(self,g,oid_to_uri,uri_to_oid,dbname,macro_filename,merge_log_filename,iterative_log_filename,log_factor,dbSerializationName,num_merges_to_log,remove_one_degree,merge_identical)

    def generate_original_unvisited(self):
        return self.super_nodes.copy()

    def node_select(self, s):
        return random.sample(s,1)[0]

    def filter_merge_candidates(self, u, merge_candidates):
        best_suv = 0
        best_node = None
        best_cost_reduction = 0
        for mc in merge_candidates:
            suv,cost_reduction = u.calc_SUV(mc)
            if suv > best_suv:
                best_suv = suv
                best_node = mc
                best_cost_reduction = cost_reduction
            #if best_suv > 0.45:
            #    break
        self.cost_reduction += best_cost_reduction
        return best_node

    def merge_supernodes(self, to_merge,u):
        if to_merge is not None:
            new_np = NP.merge(u,to_merge,self.name_table)
            return new_np
        else:
            return None

    def update_unvisited(self, unvisited, to_merge, u, merged_node):
        #print unvisited
        unvisited.remove(u)
        if to_merge is not None:
            unvisited.remove(to_merge)
            self.super_nodes.remove(u)
            self.super_nodes.remove(to_merge)
        if merged_node is not None:
            unvisited.add(merged_node)
            self.super_nodes.add(merged_node)
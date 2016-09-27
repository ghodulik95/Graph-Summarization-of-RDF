from CustomGraph import AbstractCustomGraphSummary
from CustomGraph import Node_Name_Table as NNT
from CustomGraph import Node_Profile as NP
import random

class UniformRandomCustom(AbstractCustomGraphSummary):
    def __init__(self, g,uri_to_oid,dbname):
        AbstractCustomGraphSummary.__init__(self,g,uri_to_oid,dbname)

    def generate_original_unvisited(self):
        return self.super_nodes.copy()

    def node_select(self, s):
        return random.sample(s,1)[0]

    def get_merge_candidates(self, u):
        return u.get_two_hop_neighbors()

    def filter_merge_candidates(self, u, merge_candidates):
        best_suv = 0
        best_node = None
        for mc in merge_candidates:
            suv = u.calc_SUV(mc)
            if suv > best_suv:
                best_suv = suv
                best_node = mc
            if best_suv > 0.45:
                break
        return best_node

    def merge_supernodes(self, to_merge,u):
        if to_merge is not None:
            new_np = NP.merge(u,to_merge,self.name_table)
            return new_np
        else:
            return None

    def update_unvisited(self, unvisited, to_merge, u, merged_node):
        unvisited.remove(u)
        if to_merge is not None:
            unvisited.remove(to_merge)
            self.super_nodes.remove(u)
            self.super_nodes.remove(to_merge)
        if merged_node is not None:
            unvisited.add(merged_node)
            self.super_nodes.add(merged_node)
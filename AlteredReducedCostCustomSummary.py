from CustomGraph import AbstractCustomGraphSummary
from CustomGraph import Node_Name_Table as NNT
from CustomGraph import Node_Profile as NP
import random


class AlteredReducedCostCustomSummary(AbstractCustomGraphSummary):
    def __init__(self, g, oid_to_uri, uri_to_oid, dbname, macro_filename, merge_log_filename, iterative_log_filename,log_factor,initial_rc_cutoff,num_allowable_skips,step,dbSerializationName,num_merges_to_log,remove_one_degree=False,merge_identical=False,early_terminate=None):
        self.initial_rc_cutoff = initial_rc_cutoff
        self.num_allowable_skips = num_allowable_skips
        self.step = step
        self.cur_skips = 0
        self.cur_cutoff = self.initial_rc_cutoff
        self.num_iterations = 0
        self.zero_cutoff = self.initial_rc_cutoff == 0
        AbstractCustomGraphSummary.__init__(self, g, oid_to_uri, uri_to_oid, dbname, macro_filename, merge_log_filename,
                                            iterative_log_filename, log_factor,dbSerializationName,num_merges_to_log,remove_one_degree=False,merge_identical=False,early_terminate=early_terminate)

    def get_iterative_headers(self):
        return "Time,PercentFinished,Cost,CompressionRatio,Cutoff"

    def get_iterative_entry(self,time_elapsed, unvisited_size, initial_unvisited_size):
        return "%d,%f,%d,%f,%f" % (time_elapsed,1 - float(unvisited_size)/initial_unvisited_size, self.get_iterative_cost(), self.get_iterative_compression_ratio(),self.cur_cutoff)

    def generate_original_unvisited(self):
        return self.super_nodes.copy()

    def node_select(self, s):
        return random.sample(s, 1)[0]

    def filter_merge_candidates(self, u, merge_candidates):
        best_suv = self.cur_cutoff
        best_node = None
        best_cost_reduction = 0
        for mc in merge_candidates:
            suv, cost_reduction = u.calc_SUV(mc)
            if suv >= best_suv and suv > 0:
                best_suv = suv
                best_node = mc
                best_cost_reduction = cost_reduction

        if not self.zero_cutoff and best_node is None:
            self.cur_skips += 1
            if self.cur_skips >= self.num_allowable_skips:
                self.cur_cutoff -= self.step
                if self.cur_cutoff <= 0:
                    self.cur_cutoff = 0
                    self.zero_cutoff = True
                self.cur_skips = 0
        #print self.cur_cutoff
        self.cost_reduction += best_cost_reduction
        return best_node

    def merge_supernodes(self, to_merge, u):
        if to_merge is not None:
            new_np = NP.merge(u, to_merge, self.name_table)
            return new_np
        else:
            return None

    def update_unvisited(self, unvisited, to_merge, u, merged_node):
        if to_merge is not None or self.zero_cutoff:
            unvisited.remove(u)
            if to_merge is not None:
                if to_merge in unvisited:
                    unvisited.remove(to_merge)
                self.super_nodes.remove(u)
                self.super_nodes.remove(to_merge)
            if merged_node is not None:
                unvisited.add(merged_node)
                self.super_nodes.add(merged_node)
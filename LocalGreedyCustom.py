from __future__ import print_function
from CustomGraph import AbstractCustomGraphSummary
import heapq
import random
from Node_Profile import Node_Profile as NP
import time


class Node(object):
    def __init__(self,obj,priority):
        self.obj = obj
        self.priority = priority
        self.removed = False

    def remove(self):
        self.removed = True

    def is_removed(self):
        return self.removed

    def __hash__(self):
        return self.obj.__hash__()

    def __eq__(self,other):
        if isinstance(other,Node):
            return self.obj == other.obj and self.priority == other.priority
        raise TypeError("Cannot compare types")

    def __cmp__(self,other):
        if isinstance(other, Node):
            return -cmp(self.priority, other.priority)
        raise TypeError("Cannot compare types")

class LocalMergeHeap(object):
    def __init__(self,name_table,summary):
        """
        :type summary: LocalGreedyCustom
        :type name_table: CustomGraph.Node_Name_Table
        :param name_table:
        :return:
        """
        self.h = []
        self.name_table = name_table
        self.merges = set()
        self.nodes_with_all_twohop_added = set()
        self.completed_names = set()
        self.s = summary
        self.nodes_to_merges = {}
        self.num_removed = 0
        self.reseed()

    def clean(self):
        self.h = []
        self.merges = set()
        self.nodes_with_all_twohop_added = set()
        self.num_removed = 0

    def is_completed(self):
        return len(self.completed_names) == len(self.s.super_nodes)

    def reseed(self):
        self.clean()
        for s in self.s.super_nodes:
            if s.name not in self.completed_names:
                if s.has_positive_merge():
                    self.seed(s)
                    return
                else:
                    self.completed_names.add(s.name)

    def rebalance(self):
        new_merges = set()
        new_h = []
        for m in self.h:
            if not m.is_removed():
                new_merges.add(m.obj)
                heapq.heappush(new_h,m)
        self.h = new_h
        self.merges = new_merges
        self.num_removed = 0
        print("REBALANCED HEAP")

    def add_merge(self,merge):
        if not self.has_merge(merge):
            n = Node(merge, merge[3])
            heapq.heappush(self.h, n)
            self.merges.add(merge)
            if merge[0] not in self.nodes_to_merges:
                self.nodes_to_merges[merge[0]] = set()
            if merge[1] not in self.nodes_to_merges:
                self.nodes_to_merges[merge[1]] = set()
            self.nodes_to_merges[merge[0]].add(n)
            self.nodes_to_merges[merge[1]].add(n)

    def add_all_merges(self,snode):
        """
        :type snode: Node_Profile.Node_Profile
        :param snode:
        :return:
        """
        two_hop = snode.get_two_hop_neighbors()
        for n in two_hop:
            suv,cost = snode.calc_SUV(n)
            if suv > 0:
                merge = (snode.name,n.name,cost,suv)
                if not self.has_merge(merge):
                    self.add_merge(merge)

    def has_merge(self,merge):
        return merge in self.merges or (merge[1],merge[0],merge[2],merge[3]) in self.merges

    def seed(self,snode):
        """
        :type snode: Node_Profile.Node_Profile
        """
        if isinstance(snode, basestring):
            snode = self.name_table.get_supernode(snode)
        neighborhood = snode.get_two_hop_neighborhood()
        for n in neighborhood:
            self.add_all_merges(n)
        self.nodes_with_all_twohop_added.add(snode.name)

    def pop_to_current(self):
        while (len(self.h) > 0 and
                #(not self.name_table.is_current(self.h[0].obj[1]) or
                #     not self.name_table.is_current(self.h[0].obj[0]) or
                   (self.h[0].is_removed())):
            heapq.heappop(self.h)
            self.num_removed -= 1

    def peek(self):
        self.pop_to_current()
        if len(self.h) == 0:
            self.reseed()
        elif len(self.h) > 100 and self.num_removed >= 0.5*len(self.h):
            self.rebalance()
        if len(self.h) == 0:
            return None
        return self.h[0]

    def node_in_all_twohop(self,merge):
        return merge[0] in self.nodes_with_all_twohop_added and merge[1] in self.nodes_with_all_twohop_added

    def pop(self):
        p = self.peek().obj

        while not self.node_in_all_twohop(p):
            self.seed(p[0])
            self.seed(p[1])
            p = self.peek().obj

        return heapq.heappop(self.h).obj

    def remove_related_merges(self,snode):
        """
        :type snode: Node_Profile.Node_Profile
        :param snode:
        :return:
        """
        for n in self.nodes_to_merges[snode.name]:
            if not n.is_removed():
                n.remove()
                self.num_removed += 1
        self.nodes_to_merges[snode.name] = set()
        for n in snode.neighbor_names:
            if n in self.nodes_to_merges:
                for m in self.nodes_to_merges[n]:
                    if not m.is_removed():
                        m.remove()
                        self.num_removed += 1
            self.nodes_to_merges[n] = set()

    def update_related_merges(self,merged):
        self.add_all_merges(merged)
        for n in merged.neighbor_names:
            sn = self.name_table.get_supernode(n)
            sn.update_neighbors()
            self.add_all_merges(sn)
        self.nodes_with_all_twohop_added.add(merged.name)




class LocalGreedyCustom(AbstractCustomGraphSummary):

    def generate_original_unvisited(self):
        return LocalMergeHeap(self.name_table,self)

    def node_select(self, s):
        return s.pop()

    def merge_supernodes(self, to_merge,u,unvisited):
        unvisited.remove_related_merges(to_merge[0])
        unvisited.remove_related_merges(to_merge[1])
        self.super_nodes.remove(to_merge[0])
        self.super_nodes.remove(to_merge[1])
        merged = NP.merge(to_merge[0],to_merge[1],self.name_table)
        self.super_nodes.add(merged)
        unvisited.update_related_merges(merged)

    def update_unvisited(self, unvisited, to_merge, u, merged):
        self.super_nodes.remove(to_merge[0])
        self.super_nodes.remove(to_merge[1])
        self.super_nodes.add(merged)
        #unvisited.remove_related_merges(to_merge[0])
        #unvisited.remove_related_merges(to_merge[1])
        unvisited.update_related_merges(merged)

    def get_iterative_headers(self):
        return "Time,Cost,CompressionRatio"

    def iterative_logging(self,time_elapsed,do_not_log_merges=False):
        if self.iterative is not None:
            print("%d,%d,%f" % (time_elapsed,self.get_iterative_cost(),self.get_iterative_compression_ratio()), file=self.iterative)
            self.iterative.flush()

    def summarize(self):
        self.initial_logging()
        unvisited = self.generate_original_unvisited()
        start = time.time()
        #initial_unvisited_size = len(unvisited)
        next_time_to_log = 0

        while not unvisited.is_completed():
            #print "Unvisited: " + str(len(unvisited))
            u = self.node_select(unvisited)
            #merge_candidates = self.get_merge_candidates(u)
            to_merge = [self.name_table.get_supernode(u[0]), self.name_table.get_supernode(u[1])] #self.filter_merge_candidates(u, merge_candidates)
            self.cost_reduction += u[2]
            #to_merge.add(u)
            # print(to_merge)
            self.merge_supernodes(to_merge,u,unvisited)
            #merged_node = self.merge_supernodes(to_merge, u, unvisited)
            #self.update_unvisited(unvisited, to_merge, u, merged_node)
            #if num_iterations < 100 or True:
            #    print(num_iterations)
            """perc_done = float(initial_unvisited_size - len(unvisited)) / float(initial_unvisited_size)
            if perc_done >= next_time_to_log: #self.factor_to_log is not None and num_iterations % self.factor_to_log == 0:
                next_time_to_log += self.iterative_log_factor
                now = time.time()
                time_elapsed = now - start
                total_time = 'NA'
                remainder = 'NA'
                if initial_unvisited_size != len(unvisited):
                    total_time = time_elapsed * float(initial_unvisited_size) / float(initial_unvisited_size - len(unvisited))
                    remainder = total_time - time_elapsed
                #print("Elapsed time: %d, Estimated Time Remaining: %f" % (time_elapsed, remainder))
                print(self.macro_filename + " " + "Elapsed time: %d, PercDone %f, Estimated Time Remaining: %s" % (time_elapsed, perc_done,str(remainder)))
                self.iterative_logging(time_elapsed, len(unvisited), initial_unvisited_size, unvisited)"""
            now = time.time()
            time_elapsed = now - start
            if self.num_iterations % 10 == 1:
                print(self.macro_filename + "Elapsed time: %d" % (time_elapsed))
                self.iterative_logging(time_elapsed,do_not_log_merges=True)
            if self.early_terminate is not None and time_elapsed >= self.early_terminate:
                print(self.macro_filename + " " + "Terminating early")
                break

            self.num_iterations += 1
            #print self.num_iterations
            unvisited.peek()
        self.summarize_time = time.time() - start
        self.iterative_logging(self.summarize_time,do_not_log_merges=True)
        #self.final_logging(num_iterations, 0)
        #self.name_to_profile = {v['name']:Node_Profile(v,g,self.name_table) for v in g.vs}



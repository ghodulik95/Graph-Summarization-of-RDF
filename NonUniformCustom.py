from UniformRandomCustom import UniformRandomCustom
import Scorer
from Node_Profile import Node_Profile as NP
from Node_Profile import ScoredRandomUnvisitedSet as SRUS

class NonUniformRandomCustom(UniformRandomCustom):
    def __init__(self, g, oid_to_uri, uri_to_oid, dbname, macro_filename, merge_log_filename, iterative_log_filename,
                 log_factor, dbSerializationName, num_merges_to_log, remove_one_degree=False, merge_identical=False,
                 early_terminate=None, make_summary=True):
        UniformRandomCustom.__init__(self, g, oid_to_uri, uri_to_oid, dbname, macro_filename, merge_log_filename,
                                            iterative_log_filename, log_factor, dbSerializationName, num_merges_to_log,
                                            remove_one_degree, merge_identical, early_terminate=early_terminate,
                                            make_summary=make_summary)

    def on_before_summarization(self):
        UniformRandomCustom.on_before_summarization(self)
        self.log_merges = False

    def generate_original_unvisited(self):
        univisted = None
        if self.dbname == "DBLP4":
            scorer = Scorer.DBLPScorer(self.merge_logger.node_data,self.merge_logger.uri_to_oid)
            unvisited = SRUS(scorer,self.super_nodes)
        elif self.dbname == "wordnet":
            scorer = Scorer.WordnetScorer(self.merge_logger.node_data, self.merge_logger.uri_to_oid)
            unvisited = SRUS(scorer, self.super_nodes)
        elif self.dbname == "IMDBSmall":
            scorer = Scorer.IMDBScorer(self.merge_logger.node_data, self.merge_logger.uri_to_oid)
            unvisited = SRUS(scorer, self.super_nodes)
        else:
            raise TypeError()
        return unvisited

    def node_select(self, s):
        return self.name_table.get_supernode(s.pop())

    def merge_supernodes(self, to_merge, u):
        if to_merge is not None:
            new_np = NP.merge(u, to_merge, self.name_table)
            return new_np
        else:
            return None

    def update_unvisited(self, unvisited, to_merge, u, merged_node):
        # print unvisited
        unvisited.remove(u)
        if to_merge is not None:
            if to_merge in unvisited:
                unvisited.remove(to_merge)
            self.super_nodes.remove(u)
            self.super_nodes.remove(to_merge)
        if merged_node is not None:
            unvisited.add(merged_node)
            self.super_nodes.add(merged_node)

from Abstract_Node_Filterer import Abstract_Node_Filterer

class Dense_Subgraphs_Filterer(Abstract_Node_Filterer):
    def __init__(self,graph):
        Abstract_Node_Filterer.__init__(self)
        self.g = graph

    #Here, a candidate is an original node id
    def filter_nodes(self,oid,candidate_ids):
        to_merge = set()
        o_neighbors = set(self.g.neighbors(oid))
        for candidate_id in candidate_ids:
            candidate_neighbors = self.g.neighbors(candidate_id)
            common_neighbors = o_neighbors.intersection(candidate_neighbors)
            all_neighbors = o_neighbors.union(candidate_neighbors)
            uncommon_neighbors = all_neighbors.difference(common_neighbors)
            percent_common = float(len(common_neighbors)) / len(all_neighbors)
            percent_uncommon = float(len(uncommon_neighbors)) / len(all_neighbors)
            if percent_common > percent_uncommon:
                to_merge.add(candidate_id)
        return to_merge




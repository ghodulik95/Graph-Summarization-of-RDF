class Abstract_Node_Filterer(object):
    def __init__(self):
        self.cost_reduction = 0

    def filter_nodes(self,supernode_name,candidate_names):
        raise NotImplementedError()

    def make_contains_bold(self,supernode_name,graph_summary):
        snode = graph_summary.s.vs.find(supernode_name)
        for n in snode['contains']:
            graph_summary.g.vs[n]['bold'] = True
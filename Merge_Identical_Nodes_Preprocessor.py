from Abstract_Summary_Preprocessor import Abstract_Summary_Preprocessor

class Merge_Identical_Nodes_Preprocessor(Abstract_Summary_Preprocessor):
    def __init__(self,graph_summary):
        Abstract_Summary_Preprocessor.__init__(self,graph_summary)
        self.neighbors_to_nodes = {}

    #def pre_process(self):



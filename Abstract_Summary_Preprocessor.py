from Graph_Summary import Abstract_Graph_Summary

class Abstract_Summary_Preprocessor(object):
    def __init__(self,graph_summary):
        """
        :param graph_summary:
        :type graph_summary: Abstract_Graph_Summary
        """
        self.graph_summary=graph_summary

    def pre_process(self):
        raise NotImplementedError()
from __future__ import print_function
#from Graph_Summary import Abstract_Graph_Summary
class Abstract_Merge_Logger(object):
    def __init__(self,log_file,graph_summary):
        """
        :param log_file:
        :type log_file: file
        :type graph_summary: Abstract_Graph_Summary
        """
        self.log_file = log_file
        self.graph_summary=graph_summary
        self.log_csv_headers()
        self.node_data = {}
        self.build_node_data()

    def build_node_data(self):
        return None

    def log_csv_headers(self):
        headers = self.get_csv_headers()
        h = ""
        for header in headers:
            if isinstance(header,basestring):
                h += header + ","
            else:
                h += header[0] + ","
        h = h[:-1]
        print(h,file=self.log_file)

    def get_csv_headers(self):
        raise NotImplementedError()

    def log_state_sample(self):
        raise NotImplementedError()

    def log_merge(self,u,nodes):
        """
        :param u:
        :param nodes:
        :type u: basestring
        :type nodes: set
        :return:
        """
        raise NotImplementedError()
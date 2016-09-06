from Abstract_Merge_Logger import Abstract_Merge_Logger
from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer

class Group_Merge_Logger(Abstract_Merge_Logger):
    def __init__(self,log_file,graph_summary):
        Abstract_Merge_Logger.__init__(self,log_file)
        self.suv_tools = Abstract_Reduced_Cost_Based_Node_Filterer(graph_summary)
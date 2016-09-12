from Group_Reduced_Cost_Summary import Single_Sweep_Group_Reduced_Cost_Summary
from Group_Reduced_Cost_Node_Filterer import Single_Sweep_Group_Reduced_Cost_Node_Filterer
from Uniform_Random_Node_Selector import Uniform_Random_Node_Selector

class Single_Sweep_Group_Altered_Reduced_Cost_Summary(Single_Sweep_Group_Reduced_Cost_Summary):

    def on_before_summarization(self):
        self.node_selector = Uniform_Random_Node_Selector()
        self.node_filterer = Single_Sweep_Group_Reduced_Cost_Node_Filterer(self,0.5,10,0.01)
from Abstract_Node_Selector import Abstract_Node_Selector
import random

class Uniform_Random_Node_Selector(Abstract_Node_Selector):
    def __init__(self):
        Abstract_Node_Selector.__init__(self)

    def select_node(self,unvisited):
        return random.sample(unvisited,1)[0]
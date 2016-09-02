from Abstract_Node_Filterer import Abstract_Node_Filterer
from Graph_Summary import Abstract_Graph_Summary

class Abstract_Reduced_Cost_Based_Node_Filterer(Abstract_Node_Filterer):
    def __init__(self,graph_summary):
        """
        :param graph_summary:
        :type graph_summary: Abstract_Graph_Summary
        """
        Abstract_Node_Filterer.__init__(self)
        self.graph_summary = graph_summary

    def calc_SUV(self,u_name,v_name):
        u_cost = self.get_cost(u_name)
        v_cost = self.get_cost(v_name)
        assert u_cost >= 0
        assert v_cost >= 0

        joined_cost = self.get_joined_cost(u_name,v_name)

        return float(u_cost + v_cost - joined_cost) / float(u_cost + v_cost )
        return float(u_cost + v_cost - joined_cost) / float(u_cost + v_cost )

    def get_cost(self,supernode_name):
        super_neighbors = self.graph_summary.exact_n_hop_neighbors(supernode_name,1)
        cost = 0
        for sn in super_neighbors:
            potential = self.graph_summary.get_potential_number_of_connections_in_original(supernode_name,sn)
            actual = self.graph_summary.get_number_of_connections_in_original(supernode_name,sn)
            assert actual <= potential

            if potential - actual + 1 <= actual:
                cost += potential - actual + 1
            else:
                cost += actual
        return cost

    def get_joined_potential(self,u_name,v_name,s):
        u_potential = self.graph_summary.get_potential_number_of_connections_in_original(u_name,s)
        v_potential = self.graph_summary.get_potential_number_of_connections_in_original(v_name,s)
        return u_potential + v_potential

    def get_joined_actual(self,u_name,v_name,s):
        u_actual = self.graph_summary.get_number_of_connections_in_original(u_name, s)
        v_actual = self.graph_summary.get_number_of_connections_in_original(v_name, s)
        return u_actual + v_actual

    def get_joined_cost(self,u_name,v_name):
        u_neighbors = self.graph_summary.exact_n_hop_neighbors(u_name,1)
        v_neighbors = self.graph_summary.exact_n_hop_neighbors(v_name,1)

        cost = 0
        joined_neighbors = u_neighbors.union(v_neighbors)
        for n in joined_neighbors:
            joined_potential = self.get_joined_potential(u_name,v_name,n)
            joined_actual = self.get_joined_actual(u_name,v_name,n)
            assert joined_actual <= joined_potential

            if joined_potential - joined_actual + 1 <= joined_actual:
                cost += joined_potential - joined_actual + 1
            else:
                cost += joined_actual
        return cost
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

        return float(u_cost + v_cost - joined_cost) / float(u_cost + v_cost ), u_cost + v_cost - joined_cost

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

    def get_joined_cost_from_profiles(self,p1,p2):
        potential_neighbors = p1.neighbors.union(p2.neighbors)
        cost = 0
        for n in potential_neighbors:
            a = p1.get_actual(n) + p2.get_actual(n)
            p = p1.get_potential(n) + p2.get_potential(n)
            if p - a + 1 <= a:
                cost += p - a + 1
            else:
                cost += a

        return cost

    def get_reduced_cost_from_profiles(self,p1,p2):
        cost_p1 = p1.cost
        cost_p2 = p2.cost
        cost_p1_p2 = self.get_joined_cost_from_profiles(p1,p2)
        return float(cost_p1 + cost_p2 - cost_p1_p2) / (cost_p1 + cost_p2), cost_p1 + cost_p2 - cost_p1_p2

class Node_Profile(object):
    def __init__(self,snode_name,graph_summary):
        """
        :type graph_summary: Abstract_Graph_Summary
        :param snode_name:
        :param graph_summary:
        """
        self.graph_summary = graph_summary
        snode_obj = graph_summary.s.vs.find(snode_name)
        self.size = len(snode_obj['contains'])
        self.neighbors = graph_summary.exact_n_hop_neighbors(snode_name,1)
        self.actual_connections = {}
        self.potential_connections = {}
        self.cost = 0
        for n in self.neighbors:
            a = graph_summary.get_number_of_connections_in_original(snode_name,n)
            p = graph_summary.get_potential_number_of_connections_in_original(snode_name,n)
            self.actual_connections[n] = a
            self.potential_connections[n] = p
            if p - a + 1 <= a:
                self.cost += p - a + 1
            else:
                self.cost += a

    def merge_with(self,p):
        new_neighbors = p.neighbors.difference(self.neighbors)
        all_neighbors = p.neighbors.union(self.neighbors)
        for n in all_neighbors:
            self.actual_connections[n] = p.get_actual(n) + self.get_actual(n)
            #self.potential_connections[n] = p.get_potential(n) + self.get_potential(n)
            if n in new_neighbors:
                self.potential_connections[n] = (p.size + self.size)*(int(round(float(p.potential_connections[n])/p.size)))
            else:
                self.potential_connections[n] = (p.size + self.size) * (int(round(float(self.potential_connections[n])/self.size)))
        self.size += p.size
        self.neighbors = all_neighbors


    def get_actual(self,n):
        if n in self.neighbors:
            return self.actual_connections[n]
        else:
            return 0

    def get_potential(self,n):
        if n in self.neighbors:
            return self.potential_connections[n]
        else:
            return self.size * len(self.graph_summary.s.vs.find(n)['contains'])
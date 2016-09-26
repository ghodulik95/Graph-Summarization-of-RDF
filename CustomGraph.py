import igraph as ig

class CustomGraphSummary(object):
    def __init__(self,g):
        """
        :type g: ig.Graph
        :param g:
        """
        self.name_table, self.super_nodes = Node_Name_Table.make_table_to_new_profiles(g)
        #self.name_to_profile = {v['name']:Node_Profile(v,g,self.name_table) for v in g.vs}

class Node_Name_Table(object):
    def __init__(self,graph):
        self.names = {v['name']:Node_Profile.make_node_profile_from_original_node(v,graph,self) for v in graph.vs}

    @staticmethod
    def make_table_to_new_profiles(graph):
        Node_Profile.max_supernode_index = 0
        table = Node_Name_Table(graph)
        nodes = set(table.names.values())
        return table,nodes

    def get_supernode_name(self,node_name):
        name = node_name
        while isinstance(self.names[name],basestring):
            name = self.names[name]
        return name

    def get_supernode(self,node_name):
        return self.names[self.get_supernode_name(node_name)]

    def is_current(self,name):
        return not isinstance(self.names[name],basestring)

    def get_supernode_size(self,name):
        return self.get_supernode(name).size

    def update_name(self,old_name,new_name,new_profile):
        assert self.names[old_name] is None
        self.names[old_name] = new_name
        self.names[new_name] = new_profile

    def get_all_supernodes(self):
        current_names = filter(self.is_current, self.names.keys())
        supernodes = []
        for name in current_names:
            supernodes.append(self.names[name])
        return supernodes


class Node_Profile(object):
    max_supernode_index = 0

    def __init__(self,name,name_table,size,neighbor_names,edge_connections,cost):
        """
        :type name_table: Node_Name_Table
        :param name:
        :param name_table:
        :param size:
        :param neighbor_names:
        :param edge_connections:
        :param cost:
        """
        self.name = name
        self.name_table = name_table
        self.size = size
        self.neighbor_names = neighbor_names
        self.edge_connections = edge_connections
        self.cost = cost

    def update_neighbors(self):
        updated = set()
        neighbors = self.neighbor_names.copy()
        for name in neighbors:
            if not self.name_table.is_current(name):
                new_node = self.name_table.get_supernode(name)
                new_name = new_node.name
                if new_name not in updated:
                    self.neighbor_names.add(new_name)
                    self.edge_connections[new_name] = new_node.edge_connections[self.name]
                    self.cost += self.edge_connections[new_name][2]
                    updated.add(new_name)
                self.neighbor_names.remove(name)
                self.cost -= self.edge_connections[name][2]
                del self.edge_connections[name]

    def get_edge_tuple(self,neighbor):
        if neighbor in self.neighbor_names.keys():
            return self.edge_connections[neighbor]
        else:
            n_size = self.name_table.get_supernode_size(neighbor)
            return (0,self.size*n_size,0)

    def calc_SUV(self,v):
        """
        :type v: Node_Profile
        :param v:
        :return:
        """
        self.update_neighbors()
        v.update_neighbors()
        joined_neighbors = self.neighbor_names.union(v.neighbor_names)
        joined_edges = []
        for n in joined_neighbors:
            joined_edges.append(Node_Profile.merge_edge_tuple(self.get_edge_tuple(n),v.get_edge_tuple(n)))
        joined_cost = sum(t[2] for t in joined_edges)
        return float(self.cost + v.cost - joined_cost) / (self.cost + v.cost)


    @staticmethod
    def merge_edge_tuple(t1,t2):
        a = t1[0] + t2[0]
        p = t1[1] + t2[1]
        cost = None
        if p - a + 1 <= a:
            cost = p - a + 1
        else:
            cost = a
        return (a,p,cost)

    @staticmethod
    def make_node_profile_from_original_node(v_obj,graph,name_table):
        """
        :type graph: ig.Graph
        :type name_table: Node_Name_Table
        :param snode_name:
        :param graph_summary:
        """
        name = v_obj['name']
        name_table = name_table
        size = 1
        neighbor_inds = graph.neighbors(v_obj.index)
        neighbor_names = set(graph.vs.select(neighbor_inds)['name'])
        #Tuple is Actual connections, potential connections, cost of edge
        edge_connections = {name:(1,1,1) for name in neighbor_names}
        cost = len(neighbor_names)
        return Node_Profile(name,name_table,size,neighbor_names,edge_connections,cost)

    @staticmethod
    def merge_group(group,table):
        """
        :type table: Node_Name_Table
        :type group:  list[Node_Profile]
        :param group:
        :param table:
        :return:
        """
        all_neighbors = set()
        total_size = 0
        for n in group:
            n.update_neighbors()
            all_neighbors.update(n.neighbor_names)
            total_size += n.size

        edge_tuples = {}
        for neighbor in all_neighbors:
            total_tuple = (0,0,0)
            for node in group:
                edge_tuple = node.get_edge_tuple(neighbor)
                total_tuple = Node_Profile.merge_edge_tuple(total_tuple,edge_tuple)
            edge_tuples[neighbor] = total_tuple
        cost = sum([t[2] for t in edge_tuples.values()])
        new_name = Node_Profile.get_next_name_and_increment()
        return Node_Profile(new_name,table,total_size,all_neighbors,edge_tuples,cost)

    @staticmethod
    def merge(u,v,name_table):
        """
        :type name_table: Node_Name_Table
        :type u: Node_Profile
        :type v: Node_Profile
        :param u:
        :param v:
        :return:
        """
        u.update_neighbors()
        v.update_neighbors()
        name = Node_Profile.get_next_name_and_increment()
        size = u.size + v.size
        neighor_names = u.neighbor_names.union(v.neighbor_names)
        edge_connections = {n:Node_Profile.merge_edge_tuple(u.get_edge_tuple(n), v.get_edge_tuple(n)) for n in neighor_names}
        cost = sum([t[2] for t in edge_connections.values()])
        return Node_Profile(name,name_table,size,neighor_names,edge_connections,cost)

    @staticmethod
    def get_next_name_and_increment():
        name = "S_"+Node_Profile.max_supernode_index
        Node_Profile.max_supernode_index += 1
        return name

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

    def get_two_hop_neighbor_names(self):
        self.update_neighbors()
        two_hop = set()
        for n in self.neighbor_names:
            n_neighbors = self.name_table.get_supernode(n).neighbor_names
            n_neighbors.remove(self.name)
            two_hop.update(n_neighbors)
        return two_hop

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

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.name == other.name
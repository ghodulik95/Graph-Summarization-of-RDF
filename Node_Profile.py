class Node_Profile(object):
    max_supernode_index = 0

    def __init__(self,name,contains,name_table,size,neighbor_names,edge_connections,cost,is_original=False):
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
        self.contains = contains
        self.name_table = name_table
        self.size = size
        self.neighbor_names = neighbor_names
        self.edge_connections = edge_connections
        self.cost = cost
        self.is_original=is_original

    @staticmethod
    def make_blank_node(name,name_table,is_original=True):
        return Node_Profile(name,{name},name_table,1,set(),{},0,is_original)

    def add_original_edge_to(self,neighbor):
        if neighbor not in self.neighbor_names:
            self.cost += 1
            self.neighbor_names.add(neighbor)
            self.edge_connections[neighbor] = (1,1,1)


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
        if neighbor in self.neighbor_names:
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
        return float(self.cost + v.cost - joined_cost) / (self.cost + v.cost), self.cost + v.cost - joined_cost


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
        contains = {name}
        cost = len(neighbor_names)
        return Node_Profile(name,contains,name_table,size,neighbor_names,edge_connections,cost,is_original=True)

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
        all_contains = set()
        total_size = 0
        for n in group:
            n.update_neighbors()
            all_neighbors.update(n.neighbor_names)
            all_contains.update(n.contains)
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
        new_np = Node_Profile(new_name,all_contains,table,total_size,all_neighbors,edge_tuples,cost)
        for n in group:
            table.update_name(n.name,new_name,new_np)
        return new_np

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
        contains = u.contains.union(v.contains)
        size = u.size + v.size
        neighor_names = u.neighbor_names.union(v.neighbor_names)
        edge_connections = {n:Node_Profile.merge_edge_tuple(u.get_edge_tuple(n), v.get_edge_tuple(n)) for n in neighor_names}
        cost = sum([t[2] for t in edge_connections.values()])
        new_np = Node_Profile(name,contains,name_table,size,neighor_names,edge_connections,cost)
        name_table.update_name(u.name ,name,new_np)
        name_table.update_name(v.name, name,new_np)
        return new_np

    @staticmethod
    def get_next_name_and_increment():
        name = "S_"+str(Node_Profile.max_supernode_index)
        Node_Profile.max_supernode_index += 1
        return name

    def get_two_hop_neighbor_names(self):
        self.update_neighbors()
        two_hop = set()
        for n in self.neighbor_names:
            n_snode = self.name_table.get_supernode(n)
            n_snode.update_neighbors()
            two_hop.update(n_snode.neighbor_names)
        two_hop.remove(self.name)
        return two_hop

    def get_two_hop_neighbors(self):
        names = self.get_two_hop_neighbor_names()
        neighbors = set()
        for n in names:
            neighbors.add(self.name_table.get_supernode(n))
        return neighbors

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.name == other.name
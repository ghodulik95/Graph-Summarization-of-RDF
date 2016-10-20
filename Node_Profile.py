import operator as op
import heapq
import random
import time
class Node_Profile(object):
    max_supernode_index = 0

    def __init__(self,name,contains,name_table,size,neighbor_names,edge_connections,cost,self_loop_tuple,is_original=False):
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
        self.self_loop_tuple = self_loop_tuple

    @staticmethod
    def make_blank_node(name,name_table,is_original=True):
        return Node_Profile(name,{name},name_table,1,set(),{},0,(0,1,0),is_original=is_original)

    def add_original_edge_to(self,neighbor):
        if neighbor not in self.neighbor_names and neighbor != self.name:
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
                    #print self.edge_connections
                    #print self.name
                    #print new_name
                    #print new_node.edge_connections
                    if self.name == new_name:
                        print "THIS SHOULDNT HAPPEN"
                        """t = self.edge_connections[self.name]
                        a = t[0] if t[0] != 0 else 1
                        p = ncr(self.size,2)
                        cost = None
                        if p - a + 1 <= a:
                            cost = p - a + 1
                        else:
                            cost = a
                        self.edge_connections[new_name] = (a,p,cost)"""
                    self.edge_connections[new_name] = new_node.edge_connections[self.name]
                    self.cost += self.edge_connections[new_name][2]
                    updated.add(new_name)
                self.neighbor_names.remove(name)
                self.cost -= self.edge_connections[name][2]
                del self.edge_connections[name]

    def get_edge_tuple(self,neighbor):
        if neighbor in self.neighbor_names:
            return self.edge_connections[neighbor]
        elif neighbor == self.name:
            return self.self_loop_tuple
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
        if self.name in joined_neighbors:
            joined_neighbors.remove(self.name)
        if v.name in joined_neighbors:
            joined_neighbors.remove(v.name)

        self_loop_tuple = Node_Profile.get_merged_self_loop_tuple(self,v)
        joined_cost = self_loop_tuple[2]
        for n in joined_neighbors:
            joined_cost += Node_Profile.merge_edge_tuple(self.get_edge_tuple(n),v.get_edge_tuple(n))[2]
        return float(self.cost + v.cost - joined_cost) / (self.cost + v.cost), self.cost + v.cost - joined_cost


    @staticmethod
    def merge_edge_tuple(t1, t2):
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
        curr_profile = group.pop()
        for node in group:
            curr_profile = Node_Profile.merge(curr_profile,node,table)
        return curr_profile
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
        return new_np"""

    @staticmethod
    def get_merged_self_loop_tuple(u,v):
        """
        :type u: Node_Profile
        :type v: Node_Profile
        :param u:
        :param v:
        :return:
        """
        self_loop_actual = u.self_loop_tuple[0] + v.self_loop_tuple[0]
        if u.name in v.neighbor_names or v.name in u.neighbor_names:
            u_tuple = u.get_edge_tuple(v.name)
            v_tuple = v.get_edge_tuple(u.name)
            assert u_tuple[0] == v_tuple[0]
            self_loop_actual += u_tuple[0]
        self_loop_potential = ncr(u.size + v.size, 2)
        self_loop_cost = self_loop_actual
        if self_loop_potential - self_loop_actual + 1 <= self_loop_actual:
            self_loop_cost = self_loop_potential - self_loop_actual + 1
        return self_loop_actual,self_loop_potential,self_loop_cost

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
        neighbor_names = u.neighbor_names.union(v.neighbor_names)
        if u.name in neighbor_names:
            neighbor_names.remove(u.name)
        if v.name in neighbor_names:
            neighbor_names.remove(v.name)
        edge_connections = {n:Node_Profile.merge_edge_tuple(u.get_edge_tuple(n), v.get_edge_tuple(n)) for n in neighbor_names}

        self_loop_tuple = Node_Profile.get_merged_self_loop_tuple(u,v)

        cost = sum([t[2] for t in edge_connections.values()]) + self_loop_tuple[2]
        new_np = Node_Profile(name,contains,name_table,size,neighbor_names,edge_connections,cost,self_loop_tuple)
        name_table.update_name(u.name ,name,new_np)
        name_table.update_name(v.name, name,new_np)
        for neighbor_name in neighbor_names:
            name_table.get_supernode(neighbor_name).update_neighbors()
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
        if self.name in two_hop:
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

class Node(object):
    def __init___(self,obj,name,priority):
        self.obj = obj
        self.name = name
        self.priority = priority

    def __cmp__(self,other):
        if isinstance(other, Node):
            return self.priority - other.priority
        raise TypeError("Cannot compare types")

class AbstractScoredUnvisitedSet(object):
    def __init__(self, scorer):
        self.scorer = scorer

    def add(self,item):
        raise NotImplementedError()

    def remove(self,item):
        raise NotImplementedError()

    def differenceUpdate(self,item):
        raise NotImplementedError()

    def pop(self):
        raise NotImplementedError()

    def __contains__(self, item):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

class ScoredRandomUnvisitedSet(AbstractScoredUnvisitedSet):
    def __init__(self, scorer, supernodes):
        AbstractScoredUnvisitedSet.__init__(self,scorer)
        self.unvisited = []
        self.scores = []
        self.total_score = 0
        for sn in supernodes:
            self.unvisited.append(sn.name)
            score = self.scorer.score(sn)
            self.scores.append(score)
            self.total_score += score
        self.removed = set()
        random.seed(time.time())

    def add(self,item):
        self.unvisited.append(item.name)
        score = self.scorer.score(item)
        self.scores.append(score)
        self.total_score += score

    def remove(self,item):
        self.removed.add(item.name)
        if len(self.removed) >= 0.5 * len(self.unvisited):
            self.rebalance()

    def rebalance(self):
        old_unvisited = self.unvisited
        self.unvisited = []
        old_scores = self.scores
        self.scores = []
        self.total_score = 0
        for i in range(len(old_unvisited)):
            if old_unvisited[i] not in self.removed:
                self.unvisited.append(old_unvisited[i])
                score = old_scores[i]
                self.scores.append(score)
                self.total_score += score
        self.removed.clear()

    def __contains__(self, item):
        return item.name not in self.removed

    def __len__(self):
        return len(self.unvisited) - len(self.removed)

    def differenceUpdate(self,item):
        self.remove(item)

    def pick_random_node(self):
        r = random.randint(1,self.total_score)
        running_total = 0
        for i in range(len(self.scores)):
            running_total += self.scores[i]
            if r <= running_total:
                return self.unvisited[i]
        raise Exception()

    def pop(self):
        ret = self.pick_random_node()
        while ret in self.removed:
            ret = self.pick_random_node()
        return ret


class ScoredHeapUnvisitedSet(AbstractScoredUnvisitedSet):
    def __init__(self, scorer):
        AbstractScoredUnvisitedSet.__init__(self, scorer)
        self.unvisited = []
        self.removed = set()

    def add(self,item):
        n = Node(item, item.name, self.scorer.score(item))
        heapq.heappush(self.unvisited,n)

    def remove(self,item):
        self.removed.add(item.name)

    def differenceUpdate(self,item):
        self.remove(item)

    def pop(self):
        if len(self.unvisited) > 0:
            ret = heapq.heappop(self.unvisited)
            while ret.name in self.removed:
                ret = heapq.heappop(self.unvisited)
            return ret
        return None


def ncr(n, r):
    r = min(r, n - r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n - r, -1))
    denom = reduce(op.mul, xrange(1, r + 1))
    return numer // denom
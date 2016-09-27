import igraph as ig
import time
import unique_colors
import math
import pyodbc as odbc

class AbstractCustomGraphSummary(object):
    def __init__(self,g,uri_to_oid,dbname):
        """
        :type g: ig.Graph
        :param g:
        """
        self.g = g
        self.uri_to_oid = uri_to_oid
        self.name_table, self.super_nodes = Node_Name_Table.make_table_and_nodes_from_db(dbname)
        print "Table load done"
        self.on_before_summarization()
        self.additions = {}
        self.subtractions = {}
        self.summarize()
        print "Done summarizing"
        self.s, self.snode_to_index = self.make_summary()
        self.make_drawable()
        print "Finished"

    def on_before_summarization(self):
        pass

    def initial_logging(self):
        pass

    def iterative_logging(self):
        pass

    def final_logging(self):
        pass

    def add_subtractions(self,snode1,snode2):
        pass

    def add_additions(self,snode1,snode2):
        pass

    def get_supernode_label(self,snode):
        label = ""
        if not snode.is_original:
            label = snode.name+": "
        for uri in snode.contains:
            label += str(self.uri_to_oid[uri])+","
        return label[:-1]

    def make_drawable(self):
        colors = unique_colors.uniquecolors(self.s.vcount() * 2 + 2)
        for snode in self.super_nodes:
            index = self.snode_to_index[snode.name]
            self.s.vs[index]['size'] = 30 + math.log(len(snode.contains), 2) * 7
            self.s.vs[index]['label'] = self.get_supernode_label(snode)
            color = colors.pop()
            self.s.vs[index]['color'] = color
            for c_name in snode.contains:
                c_obj = self.g.vs.find(c_name)
                c_obj['color'] = color
                c_obj['label'] = self.uri_to_oid[c_name]
                c_obj['size'] = 30
        for e in self.s.es:
            if e['to_be_removed']:
                e['color'] = "white"

    def make_summary(self):
        index_to_snode = []
        snode_to_index = {}
        cur_snode_id = 0
        for supernode in self.super_nodes:
            index_to_snode.append(supernode.name)
            snode_to_index[supernode.name] = cur_snode_id
            cur_snode_id += 1
        print "Snode index done"
        snode_count = len(index_to_snode)
        edges = []
        non_edges = []
        visited = set()
        for supernode in self.super_nodes:
            print len(visited)
            for neighbor in supernode.neighbor_names:
                if neighbor not in visited:
                    t = supernode.edge_connections[neighbor]
                    a = t[0]
                    p = t[1]
                    if p - a + 1 <= a:
                        edges.append( (snode_to_index[supernode.name],snode_to_index[neighbor]) )
                        self.add_subtractions(supernode,self.name_table.get_supernode(neighbor))
                    else:
                        non_edges.append((snode_to_index[supernode.name],snode_to_index[neighbor]))
                        self.add_additions(supernode,self.name_table.get_supernode(neighbor))
            visited.add(supernode.name)
        summary = ig.Graph(directed=False)
        summary.add_vertices(snode_count)
        summary.add_edges(edges)
        print "Done adding Real edges"
        summary.es['to_be_removed'] = [False for _ in range(summary.ecount())]
        for non_edge in non_edges:
            summary.add_edge(non_edge[0],non_edge[1],to_be_removed=True)
        print "Done adding non edges"
        return summary,snode_to_index


    def summarize(self):
       # self.initial_logging()
        unvisited = self.generate_original_unvisited()
        start = time.time()
        initial_unvisited_size = len(unvisited)

        num_iterations = 0
        while len(unvisited) > 0:
            print "Unvisited: " + str(len(unvisited))
            u = self.node_select(unvisited)
            merge_candidates = self.get_merge_candidates(u)
            to_merge = self.filter_merge_candidates(u, merge_candidates)
            #to_merge.add(u)
            # print(to_merge)
            merged_node = self.merge_supernodes(to_merge, u)
            self.update_unvisited(unvisited, to_merge, u, merged_node)
            num_iterations += 1
            #if num_iterations < 100 or True:
            #    print(num_iterations)
            if num_iterations % 10 == 0 or True: #self.factor_to_log is not None and num_iterations % self.factor_to_log == 0:
                now = time.time()
                time_elapsed = now - start
                total_time = time_elapsed * float(initial_unvisited_size) / float(
                    initial_unvisited_size - len(unvisited))
                remainder = total_time - time_elapsed
                print "Elapsed time: %d, Estimated Time Remaining: %f" % (time_elapsed, remainder)
                #print(self.macro_filename + " " + "Elapsed time: %d, Estimated Time Remaining: %f" % (time_elapsed, remainder))
                #self.iterative_logging(time_elapsed, len(unvisited), initial_unvisited_size, unvisited)
            """if self.early_terminate is not None:
                time_elapsed = time.time() - start
                if time_elapsed >= self.early_terminate:
                    print(self.macro_filename + " " + "Terminating early")
                    break"""

        #self.final_logging(num_iterations, 0)
        #self.name_to_profile = {v['name']:Node_Profile(v,g,self.name_table) for v in g.vs}


    def generate_original_unvisited(self):
        raise NotImplementedError()

    def node_select(self, s):
        """
        :type s: list[Node_Profile]
        :param s:
        :return:
        """
        raise NotImplementedError()

    def get_merge_candidates(self, u):
        """
        :type u: Node_Profile
        :param u:
        :return:
        """
        raise NotImplementedError()

    def filter_merge_candidates(self, u, merge_candidates):
        """
        :type u: Node_Profile
        :type merge_candidates: list[Node_Profile]
        :param u:
        :param merge_candidates:
        :return:
        """
        raise NotImplementedError()

    def merge_supernodes(self, to_merge,u):
        """
        :type to_merge: list[Node_Profile]
        :param to_merge:
        :return:
        """
        raise NotImplementedError()

    def update_unvisited(self, unvisited, to_merge, u, merged_name):
        """
        :type univisited: list[Node_Profile]
        :type to_merge: list[Node_Profile]
        :type merged_name: basestring
        :param unvisited:
        :param to_merge:
        :param merged_name:
        :return:
        """
        raise NotImplementedError()

class Node_Name_Table(object):
    def __init__(self,graph=None):
        self.names = {}
        if graph is not None:
            num = 0
            for v in graph.vs:
                print num
                num += 1
                self.names[v['name']] = Node_Profile.make_node_profile_from_original_node(v,graph,self)
        #self.names = {v['name']:Node_Profile.make_node_profile_from_original_node(v,graph,self) for v in graph.vs}

    @staticmethod
    def make_table_and_nodes_from_db(dbname,cutoff=50, year_s=1990, year_e=1992,include_real_name=False):
        cnxn = odbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database=' + dbname + r';Trusted_Connection=yes;')
        cursor = cnxn.cursor()
        if dbname == "DBLP4" and False:
            year_start = year_s
            year_end = year_e
            lim_num_docs = cutoff
            params = (year_start, year_end, lim_num_docs)
            q = "Exec Rows_From_Year_Range @year_start = %d, @year_end = %d, @lim_num_docs = %d" % params
            cursor.execute(q)
        else:
            cursor.execute(
                """SELECT * FROM RDF WHERE [Object] NOT LIKE '%"%' AND [Object] LIKE '%[^0-9]%' AND [Subject] NOT LIKE '%"%' AND [Subject] LIKE '%[^0-9]%' AND [Object] NOT LIKE '%Disease_Annotation>%'
                AND [Object] NOT IN (SELECT TOP 12 [Object]
                                          FROM [dbo].[RDF]
                                          GROUP BY [Object]
                                          HAVING COUNT(*) >= 100
                                          ORDER BY COUNT(*) DESC)
            """)
        count = 0
        nt = Node_Name_Table()
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            subject_name = row.Subject
            predicate_name = row.Predicate
            object_name = row.Object

            # print subject_name+" "+predicate_name+" "+object_name
            if Node_Name_Table.can_skip(subject_name, predicate_name, object_name):
                continue

            if subject_name not in nt.names:
                nt.names[subject_name] = Node_Profile.make_blank_node(subject_name,nt)
            if object_name not in nt.names:
                nt.names[object_name] = Node_Profile.make_blank_node(object_name, nt)
            nt.names[subject_name].add_original_edge_to(object_name)
            nt.names[object_name].add_original_edge_to(subject_name)

            count += 1
            if count % 200 == 0:
                print count
            if dbname != "DBLP4" and count >= cutoff and False:
                break

        cnxn.close()
        return nt,set(nt.names.values())

    @staticmethod
    def can_skip(s, p, o):
        if o[0] == '"':
            return True
        return False

    @staticmethod
    def make_table_to_new_profiles(graph):
        """
        :rtype: (Node_Name_Table, list[Node_Profile])
        :param graph:
        :return:
        """
        Node_Profile.max_supernode_index = 0
        table = Node_Name_Table(graph=graph)
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
        assert isinstance(self.names[old_name],Node_Profile)
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
from __future__ import print_function
import igraph as ig
import time
import unique_colors
import math
import pyodbc as odbc
import Single_Merge_Logger
from Node_Profile import Node_Profile
from Graph_Summary import Abstract_Graph_Summary

class AbstractCustomGraphSummary(Abstract_Graph_Summary):
    def __init__(self,g,oid_to_uri,uri_to_oid,dbname,macro_filename,merge_log_filename,iterative_log_filename,log_factor,dbSerializationName,correction_both_directions=False):
        """
        :type g: ig.Graph
        :param g:
        """
        self.g = g
        self.oid_to_uri = oid_to_uri
        self.uri_to_oid = uri_to_oid
        self.correction_both_directions = correction_both_directions
        self.macro_filename = macro_filename
        self.macro = open(macro_filename,"w")
        self.merge_log = open(merge_log_filename,"w")
        self.iterative = open(iterative_log_filename,"w")
        self.iterative_log_factor = log_factor

        self.merge_logger = Single_Merge_Logger.Single_Merge_Logger(self.merge_log, self,dbSerializationName)
        self.name_table, self.super_nodes = Node_Name_Table.make_table_and_nodes_from_db(dbname,fulldb=False)
        #print "Table load done"
        self.on_before_summarization()
        self.additions = {}
        self.subtractions = {}
        self.cost_reduction = 0
        self.summarize_time = -1
        self.num_iterations = 0
        self.summarize()
        self.s, self.snode_to_index, self.oid_to_sname = self.make_summary()
        #print "Done summarizing"
        self.final_logging()
        self.macro.close()
        self.merge_log.close()
        self.iterative.close()
        self.make_drawable()
        #print "Finished"

    def on_before_summarization(self):
        pass

    def add_subtractions(self, u, v):
        for in_u in u.contains:
            u_oid = self.uri_to_oid[in_u]
            for in_v in v.contains:
                v_oid = self.uri_to_oid[in_v]
                if not self.g.are_connected(u_oid, v_oid):
                    self.add_correction(u_oid, v_oid, self.subtractions)

    def add_additions(self, u, v):
        for in_u in u.contains:
            u_oid = self.uri_to_oid[in_u]
            for in_v in v.contains:
                v_oid = self.uri_to_oid[in_v]
                if self.g.are_connected(u_oid, v_oid):
                    self.add_correction(u_oid, v_oid, self.additions)

    def add_correction(self, u, v, correction_dict):
        self.add_correction_with_direction(u, v, correction_dict)
        if self.correction_both_directions:
            self.add_correction_with_direction(v, u, correction_dict)

    def add_correction_with_direction(self, u, v, correction_dict):
        if not correction_dict.has_key(u):
            correction_dict[u] = set()
        correction_dict[u].add(v)

    def exact_n_hop_original_neighbors_from_supernode_name(self,node,n):
        """
        :type node: Node_Profile
        :param node:
        :param n:
        :return:
        """
        if n == 1:
            neighbor_ids = set()
            for c in node.contains:
                neighbor_ids.add(self.uri_to_oid[c])
            return neighbor_ids
        elif n == 2:
            neighbor_ids = set()
            for two_hop in node.get_two_hop_neighbors():
                for c in two_hop.contais:
                    neighbor_ids.add(self.uri_to_oid[c])
            return neighbor_ids
        else:
            raise NotImplementedError()

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
        #print "Snode index done"
        snode_count = len(index_to_snode)
        edges = []
        non_edges = []
        visited = set()
        for supernode in self.super_nodes:
            #print(len(visited))
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
            if supernode.self_loop_tuple[0] > 0:
                t = supernode.self_loop_tuple
                a = t[0]
                p = t[1]
                if p - a + 1 <= a:
                    edges.append((snode_to_index[supernode.name], snode_to_index[supernode.name]))
                    self.add_subtractions(supernode, supernode)
                else:
                    #non_edges.append((snode_to_index[supernode.name], snode_to_index[neighbor])) #This shouldn't be necessary for self loops
                    self.add_additions(supernode, supernode)
            visited.add(supernode.name)
        summary = ig.Graph(directed=False)
        summary.add_vertices(snode_count)
        summary.vs['name'] = [index_to_snode[i] for i in range(snode_count)]
        summary.add_edges(edges)
        #print "Done adding Real edges"
        summary.es['to_be_removed'] = [False for _ in range(summary.ecount())]
        for non_edge in non_edges:
            summary.add_edge(non_edge[0],non_edge[1],to_be_removed=True)
        oid_to_snode = [self.name_table.get_supernode_name(self.oid_to_uri[i]) for i in range(self.g.vcount())]
        #print "Done adding non edges"
        return summary,snode_to_index,oid_to_snode


    def summarize(self):
        self.initial_logging()
        unvisited = self.generate_original_unvisited()
        start = time.time()
        initial_unvisited_size = len(unvisited)
        next_time_to_log = self.iterative_log_factor

        while len(unvisited) > 0:
            #print "Unvisited: " + str(len(unvisited))
            u = self.node_select(unvisited)
            merge_candidates = self.get_merge_candidates(u)
            to_merge = self.filter_merge_candidates(u, merge_candidates)
            #to_merge.add(u)
            # print(to_merge)
            merged_node = self.merge_supernodes(to_merge, u)
            self.update_unvisited(unvisited, to_merge, u, merged_node)
            #if num_iterations < 100 or True:
            #    print(num_iterations)
            perc_done = float(initial_unvisited_size - len(unvisited)) / float(initial_unvisited_size)
            print("PercDone: "+ str(perc_done))
            if perc_done >= next_time_to_log: #self.factor_to_log is not None and num_iterations % self.factor_to_log == 0:
                next_time_to_log += self.iterative_log_factor
                now = time.time()
                time_elapsed = now - start
                total_time = 'NA'
                remainder = 'NA'
                if initial_unvisited_size != len(unvisited):
                    total_time = time_elapsed * float(initial_unvisited_size) / float(initial_unvisited_size - len(unvisited))
                    remainder = total_time - time_elapsed
                print("Elapsed time: %d, Estimated Time Remaining: %f" % (time_elapsed, remainder))
                print(self.macro_filename + " " + "Elapsed time: %d, Estimated Time Remaining: %f" % (time_elapsed, remainder))
                self.iterative_logging(time_elapsed, len(unvisited), initial_unvisited_size, unvisited)
            if self.num_iterations % 100 == 0:
                now = time.time()
                time_elapsed = now - start
                total_time = 'NA'
                remainder = 'NA'
                if initial_unvisited_size != len(unvisited):
                    total_time = time_elapsed * float(initial_unvisited_size) / float(
                        initial_unvisited_size - len(unvisited))
                    remainder = total_time - time_elapsed
                print("Elapsed time: %d, Estimated Time Remaining: %s" % (time_elapsed, str(remainder)))
            """if self.early_terminate is not None:
                time_elapsed = time.time() - start
                if time_elapsed >= self.early_terminate:
                    print(self.macro_filename + " " + "Terminating early")
                    break"""
            self.num_iterations += 1

        self.summarize_time = time.time() - start

        #self.final_logging(num_iterations, 0)
        #self.name_to_profile = {v['name']:Node_Profile(v,g,self.name_table) for v in g.vs}

    def get_num_corrections(self):
        return self.get_num_additions() + self.get_num_subtractions()

    def get_num_edges_summary(self):
        count = 0
        for e in self.s.es:
            if not e['to_be_removed']:
                count += 1
        return count

    def get_summary_cost(self):
        return self.get_num_edges_summary() + self.get_num_corrections()

    def get_compression_ratio(self):
        original_cost = self.g.ecount()
        new_cost = self.get_summary_cost()
        #print(str(original_cost - new_cost))
        #print(str(self.node_filterer.cost_reduction))
        #assert original_cost - new_cost == self.node_filterer.cost_reduction
        return float(new_cost) / float(original_cost)

    def get_iterative_cost(self):
        return self.g.ecount() - self.cost_reduction

    def get_iterative_compression_ratio(self):
        return float(self.get_iterative_cost()) / self.g.ecount()

    def initial_logging(self):
        num_edges = self.g.ecount()
        num_vertices = self.g.vcount()
        print("----------Intial Graph----------", file=self.macro)
        print("Vertices: %d" % num_vertices, file=self.macro)
        print("Edges: %d" % num_edges,file=self.macro)
        #articulation_points = self.g.articulation_points()
        #print("Articulation Points: "+str(articulation_points),file=self.macro)

        if self.iterative is not None:
            print("Time,PercentFinished,Cost,CompressionRatio",file=self.iterative)

    def iterative_logging(self,time_elapsed, unvisited_size, initial_unvisited_size,unvisited):
        if self.iterative is not None:
            print("%d,%f,%d,%f" % (time_elapsed,float(unvisited_size)/initial_unvisited_size, self.get_iterative_cost(), self.get_iterative_compression_ratio()), file=self.iterative)
            self.iterative.flush()
        if self.merge_logger is not None:
            self.merge_logger.log_state_sample(time_elapsed, unvisited.copy(), 10)

    def final_logging(self):
        print("----------Summary----------",file=self.macro)
        print("Iterations: %d" % self.num_iterations, file=self.macro)
        print("Elapsed time: %d" % self.summarize_time, file=self.macro)
        print("Vertices: %d" % self.s.vcount(),file=self.macro)
        print("Edges: %d" % self.get_num_edges_summary(),file=self.macro)
        print("Additions: %d" % self.get_num_additions(),file=self.macro)
        print("Subtractions: %d" % self.get_num_subtractions(),file=self.macro)
        print("Total Corrections: %d" % self.get_num_corrections(),file=self.macro)
        print("Cost: %d" % self.get_summary_cost(),file=self.macro)
        print("Compression Ratio: %f" % self.get_compression_ratio(),file=self.macro)
        self.macro.flush()


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
                #print num
                num += 1
                self.names[v['name']] = Node_Profile.make_node_profile_from_original_node(v,graph,self)
        #self.names = {v['name']:Node_Profile.make_node_profile_from_original_node(v,graph,self) for v in graph.vs}

    @staticmethod
    def make_table_and_nodes_from_db(dbname,cutoff=50, year_s=1990, year_e=1992,include_real_name=False,fulldb=True):
        cnxn = odbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database=' + dbname + r';Trusted_Connection=yes;')
        cursor = cnxn.cursor()
        if dbname == "DBLP4" and not fulldb:
            year_start = year_s
            year_end = year_e
            lim_num_docs = cutoff
            params = (year_start, year_end, lim_num_docs)
            q = "Exec Rows_From_Year_Range @year_start = %d, @year_end = %d, @lim_num_docs = %d" % params
            cursor.execute(q)
        else:
            cursor.execute(
                """SELECT * FROM RDF WHERE [Object] NOT LIKE '%"%' AND [Object] NOT LIKE '%#%' AND [Object] LIKE '%<%' AND [Predicate] NOT LIKE '%#type%'
                AND [Object] LIKE '%[^0-9]%' AND [Subject] NOT LIKE '%"%' AND [Subject] LIKE '%[^0-9]%' AND [Object] NOT LIKE '%Disease_Annotation>%'
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
            if count % 10000 == 0:
                print(count)
            if dbname != "DBLP4" and count >= cutoff and not fulldb:
                break

        cnxn.close()
        return nt,set(nt.names.values())

    @staticmethod
    def can_skip(s, p, o):
        if o[0] == '"':
            return True
        if s == o:
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



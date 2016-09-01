import igraph as ig
import logging
import unique_colors
import math

class Abstract_Graph_Summary(object):
    def __init__(self,graph,oid_to_uri,uri_to_oid,logger_filename):
        """
        :type graph: ig.Graph
        :type oid_to_uri: Dictionary
        :type uri_to_oid: Dictionary
        """
        self.summary_finished = False
        self.g = graph
        self.oid_to_uri = oid_to_uri
        self.uri_to_oid = uri_to_oid
        logging.basicConfig(filename=logger_filename,level=logging.INFO)
        self.s = self.make_blank_summary()
        self.oid_to_sname = {}
        self.annotate_summary()

        self.additions={}
        self.subtractions={}
        self.max_id = self.g.vcount()

        self.node_selector = None
        self.node_filterer = None

    def make_blank_summary(self):
        graph = ig.Graph(directed=False)
        graph.add_vertices(self.g.vcount())
        return graph

    def get_supernode_name(self,num):
        return "S_"+str(num)

    def annotate_summary(self):
        if not self.summary_finished:
            for i in range(0,self.s.vcount()):
                self.s.vs[i]['contains'] = {i}
                self.s.vs[i]['name'] = self.get_supernode_name(i)
                self.oid_to_sname[i] = self.get_supernode_name(i)

    def node_select(self,s):
        raise NotImplementedError()

    def merge_supernodes(self,snodes):
        raise NotImplementedError()

    def get_merge_candidates(self,supernode_name):
        raise NotImplementedError()

    #Given a supernode, returns all supernodes which contain at least one node which is a two hop neighbor
    # of a node in the given supernode
    def exact_n_hop_neighbors(self,supernode_name,n):
        original_n_hop_neighbors = self.exact_n_hop_original_neighbors_from_supernode_name(supernode_name,n)
        supernodes = set([self.oid_to_sname[i] for i in original_n_hop_neighbors])
        return supernodes

    def exact_n_hop_original_neighbors_from_oid(self,oid,n):
        return self.exact_n_hop_original_neighbors_from_source({oid},n)

    def exact_n_hop_original_neighbors_from_supernode_name(self,supernode_name,n):
        supernode = self.s.vs.find(supernode_name)
        return self.exact_n_hop_original_neighbors_from_source(supernode['contains'],n)

    def exact_n_hop_original_neighbors_from_source(self,input_source,n):
        source = input_source
        for _ in range(n):
            next_hop_neighbors = set()
            for oid in source:
                neighbors = set(self.g.neighbors(oid))
                next_hop_neighbors.update(neighbors)
            source = next_hop_neighbors
        return source

    def filter_merge_candidates(self,supernode,merge_candidates):
        raise NotImplementedError()

    def get_potential_number_of_connections_in_original(self,snodename1,snodename2):
        node1Size = len(self.s.vs.find(snodename1)['contains'])
        node2Size = len(self.s.vs.find(snodename2)['contains'])
        return node1Size * node2Size

    def get_number_of_connections_in_original(self,snodename1,snodename2):
        node1Contains = self.s.vs.find(snodename1)['contains']
        node2Contains = self.s.vs.find(snodename2)['contains']
        count = 0
        for oid1 in node1Contains:
            for oid2 in node2Contains:
                if self.g.are_connected(oid1,oid2):
                    count += 1
        return count

    def add_subtractions(self,u_name,v_name):
        u = self.s.vs.find(u_name)
        v = self.s.vs.find(v_name)
        for in_u in u['contains']:
            for in_v in v['contains']:
                if not self.g.are_connected(in_u,in_v):
                    self.add_correction(in_u,in_v,self.subtractions)

    def add_additions(self,u_name,v_name):
        u = self.s.vs.find(u_name)
        v = self.s.vs.find(v_name)
        for in_u in u['contains']:
            for in_v in v['contains']:
                if self.g.are_connected(in_u,in_v):
                    self.add_correction(in_u,in_v,self.additions)

    def add_correction(self,u,v,correction_dict):
        self.add_correction_with_direction(u,v,correction_dict)
        self.add_correction_with_direction(v,u,correction_dict)

    def add_correction_with_direction(self,u,v,correction_dict):
        if not correction_dict.has_key(u):
            correction_dict[u] = set()
        correction_dict[u].add(v)

    def put_edges_in_summary(self):
        nodes_tried = set()
        self.additions.clear()
        self.subtractions.clear()
        self.s.delete_edges(self.s.es)
        for u in self.s.vs:
            u_name = u['name']
            potential_neighbors = self.exact_n_hop_neighbors(u_name,1)
            for v_name in potential_neighbors:
                if v_name not in nodes_tried:
                    pi_uv = self.get_potential_number_of_connections_in_original(u_name, v_name)
                    A_uv = self.get_number_of_connections_in_original(u_name, v_name)
                    if float(A_uv) / pi_uv > 0.5 :
                        self.s.add_edge(u_name, v_name)
                        self.add_subtractions(u_name, v_name)
                    else:
                        self.add_additions(u_name, v_name)
            nodes_tried.add(u_name)

    def get_support_of_superedge(self,u_name,v_name):
        return float(self.get_number_of_connections_in_original(u_name,v_name)) / self.get_potential_number_of_connections_in_original(u_name, v_name)

    def make_drawable(self):
        colors = unique_colors.uniquecolors(self.s.vcount() * 2 + 2)
        for n in self.s.vs:
            n['size'] = 30 + math.log(len(n['contains']), 2) * 7
            n['label'] = "%d" % (len(n['contains']))
            color = colors.pop()
            n['color'] = color
            for c in n['contains']:
                self.g.vs[c]['color'] = color
                self.g.vs[c]['label'] = "%d" % (c)
                self.g.vs[c]['size'] = 30
        for e in self.s.es:
            source_name = self.s.vs[e.source]['name']
            target_name = self.s.vs[e.target]['name']
            e['width'] = 5 * self.get_support_of_superedge(source_name, target_name)
            e['label'] = self.get_support_of_superedge(source_name, target_name)

    def update_unvisited(self,unvisited,to_merge,merged_name):
        unvisited.difference_update(to_merge)

    def generate_original_unvisited(self):
        raise NotImplementedError()

    def summarize(self):
        unvisited = self.generate_original_unvisited()

        while len(unvisited) > 0:
            u = self.node_select(unvisited)
            merge_candidates = self.get_merge_candidates(u)
            to_merge = self.filter_merge_candidates(u,merge_candidates)
            to_merge.add(u)
            merged_name = self.merge_supernodes(to_merge)
            self.update_unvisited(unvisited,to_merge, merged_name)

        self.put_edges_in_summary()
        self.make_drawable()





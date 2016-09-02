from __future__ import print_function
import igraph as ig
import unique_colors
from Abstract_Node_Filterer import Abstract_Node_Filterer
from Abstract_Node_Selector import Abstract_Node_Selector
import math

class Abstract_Graph_Summary(object):
    def __init__(self,graph,oid_to_uri,uri_to_oid,macro_filename,micro_filename):
        """
        :type graph: ig.Graph
        :type oid_to_uri: Dictionary
        :type uri_to_oid: Dictionary
        """
        self.summary_finished = False
        self.g = graph
        self.oid_to_uri = oid_to_uri
        self.uri_to_oid = uri_to_oid
        self.macro = open(macro_filename,mode="w")
        self.micro = open(micro_filename,mode="w")
        self.s = self.make_blank_summary()
        self.oid_to_sname = {}
        self.annotate_summary()

        self.additions={}
        self.subtractions={}
        self.max_id = self.g.vcount()

        self.node_selector = Abstract_Node_Selector()
        self.node_filterer = Abstract_Node_Filterer()

        self.on_before_summarization()
        self.summarize()
        self.macro.close()
        self.micro.close()

    def on_before_summarization(self):
        pass

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
        return self.node_selector.select_node(s)

    def merge_supernodes(self,snodes):
        assert len(snodes) > 1
        self.s.add_vertices(1)
        new_index = self.s.vcount() - 1
        new_name = self.get_supernode_name(self.max_id)
        self.s.vs[new_index]['name'] = new_name

        print(snodes)
        current_ids = [self.s.vs.find(name).index for name in snodes]
        new_contains = set()
        for snode in current_ids:
            new_contains.update(set(self.s.vs[snode]['contains']))
        self.s.vs[new_index]['contains'] = new_contains
        self.max_id += 1
        for oid in new_contains:
            self.oid_to_sname[oid] = new_name
        self.s.delete_vertices(current_ids)
        return new_name

    def get_merge_candidates(self,supernode_name):
        raise NotImplementedError()

    #Given a supernode, returns all supernodes which contain at least one node which is a two hop neighbor
    # of a node in the given supernode
    def exact_n_hop_neighbors(self,supernode_name,n):
        original_n_hop_neighbors = self.exact_n_hop_original_neighbors_from_supernode_name(supernode_name,n)
        supernodes = set([self.oid_to_sname[i] for i in original_n_hop_neighbors])
        if supernode_name in supernodes:
            supernodes.remove(supernode_name)
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
        return self.node_filterer.filter_nodes(supernode,merge_candidates)

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
                        self.s.add_edge(u_name, v_name,to_be_removed=False)
                        self.add_subtractions(u_name, v_name)
                    else:
                        self.s.add_edge(u_name,v_name,to_be_removed=True)
                        self.add_additions(u_name, v_name)
            nodes_tried.add(u_name)

    def get_support_of_superedge(self,u_name,v_name):
        return float(self.get_number_of_connections_in_original(u_name,v_name)) / self.get_potential_number_of_connections_in_original(u_name, v_name)

    def make_drawable(self):
        colors = unique_colors.uniquecolors(self.s.vcount() * 2 + 2)
        for n in self.s.vs:
            n['size'] = 30 + math.log(len(n['contains']), 2) * 7
            n['label'] = self.get_supernode_label(n)
            color = colors.pop()
            n['color'] = color
            for c in n['contains']:
                self.g.vs[c]['color'] = color
                self.g.vs[c]['label'] = "%d" % (c)
                self.g.vs[c]['size'] = 30
        for e in self.s.es:
            if e['to_be_removed']:
                e['color'] = "white"
            #source_name = self.s.vs[e.source]['name']
            #target_name = self.s.vs[e.target]['name']
            #e['width'] = 5 * self.get_support_of_superedge(source_name, target_name)
            #e['label'] = self.get_support_of_superedge(source_name, target_name)

    def get_supernode_label(self,supernode_object):
        contains = supernode_object['contains']
        ret = ""
        for n in contains:
            ret += str(n)+","
        return ret

    def update_unvisited(self,unvisited,to_merge,merged_name=None):
        """
        :param unvisited:
        :param to_merge:
        :param merged_name:
        :type unvisited: Set
        :type to_merge: Set
        :type merged_name: String
        :return:
        """
        unvisited.difference_update(to_merge)

    def generate_original_unvisited(self):
        return set(self.s.vs['name'])

    def summarize(self):
        self.initial_logging()
        unvisited = self.generate_original_unvisited()

        num_iterations = 0
        while len(unvisited) > 0:
            u = self.node_select(unvisited)
            merge_candidates = self.get_merge_candidates(u)
            to_merge = self.filter_merge_candidates(u,merge_candidates)
            to_merge.add(u)
            merged_name = None
            if len(to_merge) > 1:
                merged_name = self.merge_supernodes(to_merge)
            self.update_unvisited(unvisited,to_merge, merged_name)
            num_iterations += 1
        self.put_edges_in_summary()
        self.final_logging(num_iterations)
        self.make_drawable()

    def get_num_additions(self):
        #Corrections are in pairs to be easily queryable
        num_additions = sum([len(self.additions[a]) for a in self.additions.keys()])
        assert num_additions % 2 == 0
        return num_additions / 2

    def get_num_subtractions(self):
        # Corrections are in pairs to be easily queryable
        num_subtractions = sum([len(self.subtractions[a]) for a in self.subtractions.keys()])
        assert num_subtractions % 2 == 0
        return num_subtractions / 2

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
        return float(new_cost) / float(original_cost)

    def initial_logging(self):
        num_edges = self.g.ecount()
        num_vertices = self.g.vcount()
        print("----------Intial Graph----------", file=self.macro)
        print("Vertices: %d" % num_vertices, file=self.macro)
        print("Edges: %d" % num_edges,file=self.macro)

    def final_logging(self,num_iterations):
        print("----------Summary----------",file=self.macro)
        print("Vertices: %d" % self.s.vcount(),file=self.macro)
        print("Edges: %d" % self.get_num_edges_summary(),file=self.macro)
        print("Additions: %d" % self.get_num_additions(),file=self.macro)
        print("Subtractions: %d" % self.get_num_subtractions(),file=self.macro)
        print("Total Corrections: %d" % self.get_num_corrections(),file=self.macro)
        print("Cost: %d" % self.get_summary_cost(),file=self.macro)
        print("Compression Ratio: %f" % self.get_compression_ratio(),file=self.macro)




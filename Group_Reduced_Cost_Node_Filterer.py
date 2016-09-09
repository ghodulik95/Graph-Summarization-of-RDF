from Abstract_Reduced_Cost_Based_Node_Filterer import Abstract_Reduced_Cost_Based_Node_Filterer

class Single_Sweep_Group_Reduced_Cost_Node_Filterer(Abstract_Reduced_Cost_Based_Node_Filterer):

    def __init__(self,graph_summary,cutoff):
        Abstract_Reduced_Cost_Based_Node_Filterer.__init__(self,graph_summary)
        self.num_iterations = 0
        assert 0 <= cutoff and cutoff <= 1
        self.cutoff = cutoff

    def filter_nodes(self,supernode_name,candidate_names):
        assert supernode_name not in candidate_names
        merge_reduced_costs = {c_name:self.calc_SUV(supernode_name,c_name) for c_name in candidate_names}
        sorted_candidates = sorted((list(candidate_names)),key=lambda x: merge_reduced_costs[x])
        sorted_candidates = filter(lambda x: merge_reduced_costs[x] > 0, sorted_candidates)
        sorted_candidates.append(supernode_name)

        neighbor_num_connected = {}
        neighbor_potential_num_connected = {}
        contains = set()
        to_merge = set()
        curr_snode_size = 0.0
        prev_suv_ratio = 0.0
        sum_degrees = 0
        while len(sorted_candidates) > 0:
            next_candidate = sorted_candidates.pop()
            next_candidate_obj = self.graph_summary.s.vs.find(next_candidate)
            contains.update(next_candidate_obj['contains'])
            next_candidate_size = len(next_candidate_obj['contains'])
            some_oid = next_candidate_obj['contains'].pop()
            next_candidate_obj['contains'].add(some_oid)
            next_candidate_degree = self.graph_summary.g.vs[some_oid].degree()
            sum_degrees += next_candidate_degree*next_candidate_size

            neighbors = self.graph_summary.exact_n_hop_neighbors(next_candidate,1)
            for n in neighbors:
                num_actual_connections = self.graph_summary.get_number_of_connections_in_original(next_candidate,n)
                n_size = len(self.graph_summary.s.vs.find(n)['contains'])
                if n not in neighbor_num_connected:
                    neighbor_num_connected[n] = num_actual_connections
                else:
                    neighbor_num_connected[n] += num_actual_connections

                neighbor_potential_num_connected[n] = (next_candidate_size + curr_snode_size) * n_size

            curr_suv = 1.0
            best_suv = 1.0
            if len(to_merge) > 0:
                curr_suv = self.calc_SUV_from_num_dicts(neighbor_num_connected,neighbor_potential_num_connected,sum_degrees)
                best_suv = 1.0 - (1.0/(curr_snode_size+next_candidate_size))

            suv_ratio = curr_suv/best_suv
            print "%f, %f, %f" % (curr_suv,best_suv,suv_ratio)
            if len(to_merge) == 0 or (suv_ratio > self.cutoff):
                to_merge.add(next_candidate)
                curr_snode_size += float(next_candidate_size)
                if len(to_merge) != 0:
                    prev_suv_ratio = suv_ratio
            else:
                break
            print contains

        print to_merge
        self.num_iterations += 1
        if self.num_iterations % 100 == 0:
            print self.num_iterations

        return to_merge


    def calc_SUV_from_num_dicts(self,actual,potential,sum_degrees):
        cost = 0
        for n in actual.keys():
            a = actual[n]
            p = potential[n]
            assert a <= p
            if p - a + 1 <= a:
                cost += p - a + 1
            else:
                cost += a
        return 1 - (float(cost) / sum_degrees)
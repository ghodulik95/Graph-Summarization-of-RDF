from GroupUniformRandomCustom import GroupUniformRandomCustom
from Node_Profile import Node_Profile as NP


class GroupSharedNeighborsCustom(GroupUniformRandomCustom):

    def filter_merge_candidates(self, u, merge_candidates):
        assert u not in merge_candidates

        perc_shared_neighbors = {mc:u.get_perc_shared_neighbors(mc) for mc in merge_candidates}
        sorted_candidates = sorted(filter(lambda x: perc_shared_neighbors[x] > 0.5, list(perc_shared_neighbors.keys())), key=lambda y: perc_shared_neighbors[y])
        curr_snode = u
        merged = {u}

        if len(sorted_candidates) == 0:
            return merged, None

        first = True

        while len(sorted_candidates) > 0:
            candidate = sorted_candidates.pop()
            suv,cost_reduction = curr_snode.calc_SUV(candidate)
            if suv > 0:
                curr_snode = NP.merge(curr_snode,candidate,self.name_table)
                self.cost_reduction += cost_reduction
                merged.add(candidate)
            elif first:
                return merged,None
            else:
                break
            first = False
        return merged,curr_snode
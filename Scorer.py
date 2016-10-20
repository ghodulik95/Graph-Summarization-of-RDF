import numpy
class AbstractScorer(object):
    def __init__(self):
        pass

    def score(self, node_profile):
        raise NotImplementedError()

class Node_Data_Scorer(AbstractScorer):
    def __init__(self, node_data,uri_to_oid):
        AbstractScorer.__init__(self)
        self.node_data = node_data
        self.uri_to_oid = uri_to_oid
        self.attributes = self.get_attributes()

    #format: [ [[(metric, operation, bool function), ...], score], ...]
    def get_attributes(self):
        raise NotImplementedError()

    def get_snode_metric(self,contains,metric,stats):
        #print(self.node_data[metric])
        #print(self.node_data[metric][0])
        if metric == 'size':
            return len(contains)
        metrics = [self.node_data[metric][int(i)] for i in contains]
        to_return = None
        if 'max' == stats:
            to_return = max(metrics)
        if 'min' == stats:
            to_return = min(metrics)
        if 'avg' == stats:
            to_return = float(sum(metrics)) / len(metrics)
        if 'median' == stats:
            to_return = numpy.median(metrics)
        if 'deviation' == stats:
            to_return = numpy.std(metrics)
        if 'as-is' == stats:
            to_return = metrics[0]
        return to_return

    def score(self,node_profile):
        score = 1
        contains = [self.uri_to_oid[c] for c in node_profile.contains]
        for a in self.attributes:
            addScore = True
            for am in a[0]:
                val = self.get_snode_metric(contains, am[0], am[1])
                addScore = addScore and am[2](val)
            if addScore:
                score += a[1]
        return score

#For wordnet remove1degree merge identical
class WordnetScorer(Node_Data_Scorer):
    def __init__(self, node_data, uri_to_oid):
        Node_Data_Scorer.__init__(self, node_data, uri_to_oid)

    def get_attributes(self):
        return [
                    ([('degrees', 'max', lambda x: numerical_comparison(x,None,2)),
                      ('num2hop', 'min', lambda x: numerical_comparison(x,2.5,None)),
                      ('size', None, lambda x: numerical_comparison(x,1,1))], 2),
                    ([('degrees', 'max', lambda x: not numerical_comparison(x,None,2)),
                      ('articulation_proximity', 'min', lambda x: x != 0),
                      ('clustering', 'min', lambda x: numerical_comparison(x,0.13,None))], 2),
                    ([('articulation_proximity', 'min', lambda x: x == 1),
                      ('degrees', 'max', lambda x: numerical_comparison(x,None,2.5)),
                      ('num2hop', 'max', lambda x: numerical_comparison(x,2.5,None))], 2),
                    ([('articulation_proximity', 'min', lambda x: x != 1),
                      ('clustering', 'min', lambda x: numerical_comparison(x, 0.13, None))], 2)
                ]

#For DBLP4 Remove 1 degree merge identical
class DBLPScorer(Node_Data_Scorer):
    def __init__(self, node_data, uri_to_oid):
        Node_Data_Scorer.__init__(self, node_data, uri_to_oid)

    def get_attributes(self):
        return [
                    ([('clustering', 'min', lambda x: x >= 0.15)], 2),
                    ([('authority', 'deviation', lambda x: x == 0)], 2),
                    ([('deg2hopRatio', 'min', lambda x: x >= 7.2)], 2),
                    ([('deg2hopRatio', 'min', lambda x: x >= 5)], 2),
                    ([('deg2hopRatio', 'min', lambda x: x > 4.2)], 2),
                    ([('degrees', 'min', lambda x: x <= 2)], 2)
                ]

#For IMDB Small Remove 1 Degree merge identical
class IMDBScorer(Node_Data_Scorer):
    def __init__(self, node_data, uri_to_oid):
        Node_Data_Scorer.__init__(self, node_data, uri_to_oid)

    def get_attributes(self):
        return [
                    ([('degrees', 'min', lambda x: x >= 34)], 2),
                    ([('degrees', 'min', lambda x: x >= 34),
                      ('authority', 'max', lambda x: x >= 0.000000237 or x == 0)], 2),
                    ([('degrees', 'min', lambda x: x >= 21)], 1),
                    ([('num2hop', 'max', lambda x: x >= 12)], 2),
                    ([('deg2hopRatio', 'max', lambda x: x < 5.1)], 2),
                    ([('degrees', 'min', lambda x: x < 34),
                      ('deg2hopRatio', 'max', lambda x: x >= 171)], 3),
                ]

def numerical_comparison(input, min, max):
    return (min is None or min <= input) and (max is None or input <= max)

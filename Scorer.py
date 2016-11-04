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
        #print "Metric: "+metric
        #for i in contains:
        #    print i
        metrics = [self.node_data[metric][int(i)] for i in contains]
        to_return = None
        if 'max' == stats:
            to_return = max(metrics)
        elif 'min' == stats:
            to_return = min(metrics)
        elif 'avg' == stats:
            to_return = float(sum(metrics)) / len(metrics)
        elif 'median' == stats:
            to_return = numpy.median(metrics)
        elif 'deviation' == stats:
            to_return = numpy.std(metrics)
        elif 'as-is' == stats:
            to_return = metrics[0]
        else:
            raise Exception("Invalid metric given")
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

class SP2BScorer(Node_Data_Scorer):
    def __init__(self, node_data, uri_to_oid):
        Node_Data_Scorer.__init__(self, node_data, uri_to_oid)

    def get_attributes(self):
        return [
            ([('degrees', 'max', lambda x: x == 1)], 4),
            ([('degrees', 'max', lambda x: x == 2),
              ('deg2hopRatio', 'min', lambda x: x < 8)], 12),
            ([('degrees', 'max', lambda x: x >= 2),
              ('deg2hopRatio', 'min', lambda x: x >= 195)], 30),
            ([('deg2hopRatio', 'median', lambda x: x > 18),
              ('clustering', 'median', lambda x: x >= 0.026)], 20),
            ([('authority', 'max', lambda x: x < 0.0026)], 3)
        ]

class LUBMScorer(Node_Data_Scorer):
    def __init__(self, node_data, uri_to_oid):
        Node_Data_Scorer.__init__(self, node_data, uri_to_oid)

    def get_attributes(self):
        return [
            ([('deg2hopRatio', 'max', lambda x: x >= 97)], 3),
            ([('deg2hopRatio', 'max', lambda x: x >= 97),
              ('degrees', 'max', lambda x: x< 5.5)], 4),
            ([('deg2hopRatio', 'min', lambda x: x >= 109)], 3),
            ([('deg2hopRatio', 'min', lambda x: x >= 109),
              ('authority', 'max', lambda x: x < 0.000088)], 4),
            ([('deg2hopRatio', 'min', lambda x: x >= 99),
              ('size', None, lambda x: x == 1)], 3),
            ([('deg2hopRatio', 'min', lambda x: x >= 99),
              ('size', None, lambda x: x == 1),
              ('clustering', 'max', lambda x: x < 0.024)], 4)
        ]

#For wordnet remove1degree merge identical
class WordnetScorer(Node_Data_Scorer):
    def __init__(self, node_data, uri_to_oid):
        Node_Data_Scorer.__init__(self, node_data, uri_to_oid)

    def get_attributes(self):
        return [
            ([('articulation_proximity', 'min', lambda x: x == 1),
              ('degrees', 'max', lambda x: x < 2.5),
              ('num2hop', 'max', lambda x: x >= 2.5)], 3),
            ([('articulation_proximity', 'min', lambda x: x != 1),
              ('clustering', 'max', lambda x: x >= 0.14)], 20),
            ([('num2hop', 'min', lambda x: x >= 3.5)],2),
            ([('num2hop', 'min', lambda x: x >= 3.5),
              ('degrees', 'max', lambda x: x < 2.5)], 3),
            ([('num2hop', 'min', lambda x: x >= 3.5),
              ('degrees', 'max', lambda x: x < 2.5),
              ('size', None, lambda x: x == 1)], 4),
            ([('degrees', 'max', lambda x: x >= 1.5),
              ('articulation_proximity', 'min', lambda x: x != 0),
              ('clustering', 'max', lambda x: x >= 0.13)], 12)
            ]
        """
            [
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
            """

#For DBLP4 Remove 1 degree merge identical
class DBLPScorer(Node_Data_Scorer):
    def __init__(self, node_data, uri_to_oid):
        Node_Data_Scorer.__init__(self, node_data, uri_to_oid)

    def get_attributes(self):
        return [
            ([('num2hop', 'median', lambda x: x >= 5.5),
              ('size', None, lambda x: x == 1),
              ('clustering', 'max', lambda x: x >= 0.18)], 20),
            ([('deg2hopRatio', 'min', lambda x: x >= 7.5),
              ('clustering', 'min', lambda x: x >= 0.27)], 12),
            ([('deg2hopRatio', 'min', lambda x: x >= 7.5),
              ('clustering', 'min', lambda x: x >= 0.27),
              ('authority', 'deviation', lambda x: x < 0.000000000000717)], 14),
            ([('num2hop', 'min', lambda x: x >= 6.5),
              ('clustering', 'min', lambda x: x >= 0.25),
              ('authority', 'deviation', lambda x: x == 0)], 11)
        ]

        """[
                    ([('clustering', 'min', lambda x: x >= 0.15)], 2),
                    ([('authority', 'deviation', lambda x: x == 0)], 2),
                    ([('deg2hopRatio', 'min', lambda x: x >= 7.2)], 2),
                    ([('deg2hopRatio', 'min', lambda x: x >= 5)], 2),
                    ([('deg2hopRatio', 'min', lambda x: x > 4.2)], 2),
                    ([('degrees', 'min', lambda x: x <= 2)], 2)
                ]"""

#For IMDB Small Remove 1 Degree merge identical
class IMDBScorer(Node_Data_Scorer):
    def __init__(self, node_data, uri_to_oid):
        Node_Data_Scorer.__init__(self, node_data, uri_to_oid)

    def get_attributes(self):
        return [
            ([('degrees', 'max', lambda x: x >= 12)], 3),
            ([('degrees', 'max', lambda x: x >= 12),
              ('num2hop','max', lambda x: x >= 48)], 3),
            ([('degrees', 'max', lambda x: x >= 12),
              ('num2hop', 'max', lambda x: x >= 48),
              ('authority', 'max', lambda x: x >= 0.000000023)], 11),
            ([('degrees', 'min', lambda x: x >= 34)], 6),
            ([('degrees', 'min', lambda x: x >= 24)], 5),
            ([('degrees', 'min', lambda x: x >= 24),
              ('num2hop','min',lambda x: x >= 177)], 5),
            ([('authority', 'max', lambda x: x >= 0.021)], 30)
        ]

        """[
                    ([('degrees', 'min', lambda x: x >= 34)], 2),
                    ([('degrees', 'min', lambda x: x >= 34),
                      ('authority', 'max', lambda x: x >= 0.000000237 or x == 0)], 2),
                    ([('degrees', 'min', lambda x: x >= 21)], 1),
                    ([('num2hop', 'max', lambda x: x >= 12)], 2),
                    ([('deg2hopRatio', 'max', lambda x: x < 5.1)], 2),
                    ([('degrees', 'min', lambda x: x < 34),
                      ('deg2hopRatio', 'max', lambda x: x >= 171)], 3)
                ]"""

def numerical_comparison(input, min, max):
    return (min is None or min <= input) and (max is None or input <= max)

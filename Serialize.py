import cPickle
import igraph as ig
import Graph_Importer
import os.path
from multiprocessing import Process,Pool

def find_distance_to_articulation(v, neighbors, two_hop, articulation_points):
    if v in articulation_points:
        return 0, v
    n_intersect = neighbors.intersection(articulation_points)
    if len(n_intersect) > 0:
        return 1, n_intersect.pop()
    two_intersect = two_hop.intersection(articulation_points)
    if len(two_intersect) > 0:
        return 2, two_intersect.pop()
    return -1, None

def load_and_serialize_helper(args):
    load_graph_and_serialize(args[0],args[1],args[2])

def load_graph_and_serialize(dbname,fulldb,serializeName):
    print serializeName + " Started"
    graph,id_to_node_name, node_name_to_id = Graph_Importer.import_graph_regular(dbname,fulldb=fulldb)
    print "Graph imported"
    build_node_data_and_serialize(graph,node_name_to_id,serializeName)
    print serializeName + " finished"

def build_node_data_and_serialize(graph,uri_to_oid,serializeName):
    """
    :type graph: ig.Graph
    :param graph:
    :param uri_to_id:
    :return:
    """
    script_dir = os.path.dirname(__file__)
    serialization_filename = os.path.join(script_dir, "Serializations/" + serializeName + ".p")
    if os.path.isfile(serialization_filename):
        raise OSError()
    else:
        all_node_ids = range(0, graph.vcount())
        print(graph.vcount())
        print(serializeName + " " + "start")
        node_data = {}
        node_data['degrees'] = [v.degree() for v in graph.vs]
        print(serializeName + " " + "degrees done")
        articulation_points = set(graph.articulation_points())
        print(serializeName + " " + "articulation points found")
        node_data['num2hop'] = []
        node_data['deg2hopRatio'] = []
        node_data['articulation_proximity'] = []
        node_data['articulation_nearest'] = []
        for v in all_node_ids:
            neighbors = set(graph.neighbors(v))
            two_hop = set(graph.neighborhood(vertices=v, order=2))
            node_data['num2hop'].append(len(two_hop))
            if node_data['degrees'][v] > 0:
                node_data['deg2hopRatio'].append(
                    float(node_data['num2hop'][v]) / node_data['degrees'][v])
            else:
                node_data['deg2hopRatio'][v].append(-1)
            art_proximitiy, art_closest = find_distance_to_articulation(v, neighbors, two_hop, articulation_points)
            node_data['articulation_proximity'].append(art_proximitiy)
            node_data['articulation_nearest'].append(art_closest)
            # print(v)
        print(serializeName + " " + "num2hop done")
        print(serializeName + " " + "deg2hop ratio done")
        print(serializeName + " " + "articulation done")
        node_data['clustering'] = graph.transitivity_local_undirected()
        print(serializeName + " " + "clustering done")
        node_data['authority'] = graph.authority_score()
        print(serializeName + " " + "Auth score done")
        node_data['hub_score'] = graph.hub_score()
        print(serializeName + " " + "hub score done")
        # node_data['eccentricity'] = graph.g.eccentricity()
        # print("Eccentricity done")
        # node_data['closeness'] = graph.g.closeness()
        # print("Closeness done")
        serial = {'node_data': node_data, 'uri_to_oid': uri_to_oid}
        cPickle.dump(serial, open(serialization_filename, "wb"))
        print(serializeName + " " + "All done")


if __name__=='__main__':
    dbs = ["wordnet","DBLP4", "IMDBSmall", "LUBM", "SP2B"]
    fulldbs = [True for _ in dbs]
    serializeNames = [dbname+"Full" for dbname in dbs]
    params = [(dbs[i],fulldbs[i],serializeNames[i]) for i in range(len(dbs))]
    p = Pool(processes=5)
    p.map(load_and_serialize_helper, params)
from Uniform_Dense_Summary import Uniform_Dense_Summary
from Uniform_Pure_Randomized_Summary import Uniform_Pure_Randomized_Summary
from Altered_Reduced_Cost_Summary import Altered_Reduced_Cost_Summary
import Graph_Importer
import igraph as ig

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Altered_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,"AlteredMacro.txt", "AlteredMicro.txt",num_skips=10,step=0.01,initial_rc_cutoff=0.5)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("AlteredOriginal.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("AlteredSummary.png")


graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Uniform_Pure_Randomized_Summary(graph,oid_to_uri,uri_to_oid,"RandomizedMacro.txt", "RandomizedMicro.txt")

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("RandomizedOriginal.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("RandomizedSummary.png")

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Uniform_Dense_Summary(graph,oid_to_uri,uri_to_oid,"DenseMacro.txt", "DenseMicro.txt")

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("DenseOriginal.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("DenseSummary.png")
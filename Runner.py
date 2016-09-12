from Uniform_Dense_Summary import Uniform_Dense_Summary
from Uniform_Pure_Randomized_Summary import Uniform_Pure_Randomized_Summary
from Altered_Reduced_Cost_Summary import Altered_Reduced_Cost_Summary
from Group_Reduced_Cost_Summary import Single_Sweep_Group_Reduced_Cost_Summary
from Single_Sweep_Group_Altered_Reduced_Cost_Summary import Single_Sweep_Group_Altered_Reduced_Cost_Summary
import Graph_Importer
import igraph as ig

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Single_Sweep_Group_Altered_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,"GroupAlteredReducedMacro.txt", "GroupAlteredReducedMicro.txt",remove_one_degree=False)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("GroupAlteredReducedOriginal.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("GroupAlteredReducedSummary.png")

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Single_Sweep_Group_Altered_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,"GroupAlteredReducedMacro2.txt", "GroupAlteredReducedMicro2.txt",remove_one_degree=True)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("GroupAlteredReducedOriginal2.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("GroupAlteredReducedSummary2.png")

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Single_Sweep_Group_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,"GroupReducedMacro.txt", "GroupReducedMicro.txt",remove_one_degree=False)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("GroupReducedOriginal.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("GroupReducedSummary.png")

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Single_Sweep_Group_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,"GroupReducedMacro2.txt", "GroupReducedMicro2.txt",remove_one_degree=True)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("GroupReducedOriginal2.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("GroupReducedSummary2.png")
"""
graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Altered_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,"AlteredMacro2.txt", "AlteredMicro2.txt",remove_one_degree=True,num_skips=10,step=0.01,initial_rc_cutoff=0.5)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("AlteredOriginal2.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("AlteredSummary2.png")


graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Uniform_Pure_Randomized_Summary(graph,oid_to_uri,uri_to_oid,"RandomizedMacro2.txt", "RandomizedMicro2.txt",remove_one_degree=True)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("RandomizedOriginal2.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("RandomizedSummary2.png")

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Uniform_Dense_Summary(graph,oid_to_uri,uri_to_oid,"DenseMacro2.txt", "DenseMicro2.txt",remove_one_degree=True)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("DenseOriginal2.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("DenseSummary2.png")

"""
#from Uniform_Dense_Summary import Uniform_Dense_Summary
#from Uniform_Pure_Randomized_Summary import Uniform_Pure_Randomized_Summary
#from Altered_Reduced_Cost_Summary import Altered_Reduced_Cost_Summary
#from Group_Reduced_Cost_Summary import Single_Sweep_Group_Reduced_Cost_Summary
#from Single_Sweep_Group_Altered_Reduced_Cost_Summary import Single_Sweep_Group_Altered_Reduced_Cost_Summary
from LocalGreedyCustom import LocalGreedyCustom
from GroupUniformRandomCustom import GroupUniformRandomCustom
from AlteredReducedCostCustomSummary import AlteredReducedCostCustomSummary
import Graph_Importer
import Graph_Exporter
import igraph as ig
from UniformRandomCustom import UniformRandomCustom

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4",include_real_name=True,fulldb=False)
print "Import done"

g = LocalGreedyCustom(graph,oid_to_uri,uri_to_oid,"DBLP4","DBLP4LocalMacro.txt","DBLP4LocalMerge.csv","SP2BCustomIterative.csv",2,"DBLP500",10,remove_one_degree=False,merge_identical=True,early_terminate=0.9999,make_summary=True)

#Graph_Exporter.export_summary(g,"SP2B","testingExport")

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("DBLP500LocalTestOriginal.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("DBLP500LocalTestSummary.png")
"""

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")
print "Import done"

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
print "Import Done"
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

graph, oid_to_uri,uri_to_oid, = Graph_Importer.import_graph_regular("DBLP4")

g = Altered_Reduced_Cost_Summary(graph,oid_to_uri,uri_to_oid,"AlteredMacro2.txt", "AlteredMicro2.txt",correction_both_directions=False,remove_one_degree=True,num_skips=10,step=0.01,initial_rc_cutoff=0.5)
Graph_Exporter.export_summary(g,"DBLP4","test")

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

g = Uniform_Pure_Randomized_Summary(graph,oid_to_uri,uri_to_oid,"RandomizedMacro.txt", "RandomizedMicro.csv",iterative_filename="RandomizedIterative.csv",iterative_logging_factor=10,remove_one_degree=False,early_terminate=60)

layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("RandomizedOriginal1.png")

graph = g.s
layout = graph.layout("kk")
visual_style = {}
visual_style["layout"] = layout
visual_style["bbox"] = (1000, 1000)
ig.plot(graph, **visual_style).save("RandomizedSummary1.png")

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
print "Imported"
g = Uniform_Dense_Summary(graph,oid_to_uri,uri_to_oid,"DenseMacro2.txt", "DenseMicro2.txt",remove_one_degree=False)

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
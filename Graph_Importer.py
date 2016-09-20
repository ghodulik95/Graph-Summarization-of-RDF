#Graph Importer module
import pyodbc as odbc
import igraph as ig

def import_graph_regular(dbname, cutoff=500, year_s=1990, year_e=1993):
    cnxn = odbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database=' + dbname + r';Trusted_Connection=yes;')
    # cnxn.autoCommit = True
    cursor = cnxn.cursor()
    if dbname == "DBLP4" and False:
        year_start = year_s
        year_end = year_e
        lim_num_docs = cutoff
        params = (year_start, year_end, lim_num_docs)
        q = "Exec Rows_From_Year_Range @year_start = %d, @year_end = %d, @lim_num_docs = %d" % params
        cursor.execute(q)
    else:
        cursor.execute(
            """SELECT * FROM RDF WHERE [Object] NOT LIKE '%"%' AND [Object] LIKE '%[^0-9]%' AND [Subject] NOT LIKE '%"%' AND [Subject] LIKE '%[^0-9]%' AND [Object] NOT LIKE '%Disease_Annotation>%'""")

    node_name_to_id = {}
    id_to_node_name = {}
    edges = set()
    max_node_id = -1
    count = 0
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        subject_name = row.Subject
        predicate_name = row.Predicate
        object_name = row.Object

        # print subject_name+" "+predicate_name+" "+object_name
        if can_skip(subject_name, predicate_name, object_name):
            continue

        if not node_name_to_id.has_key(subject_name):
            max_node_id += 1
            node_name_to_id[subject_name] = max_node_id
            id_to_node_name[max_node_id] = subject_name
        if not node_name_to_id.has_key(object_name):
            max_node_id += 1
            node_name_to_id[object_name] = max_node_id
            id_to_node_name[max_node_id] = object_name
        edges.add((node_name_to_id[subject_name], node_name_to_id[object_name]))
        count += 1
        if dbname != "DBLP4" and count >= cutoff and False:
            break

    cnxn.close()

    g = ig.Graph(directed=False)
    g.add_vertices(max_node_id + 1)
    g.add_edges(edges)

    return g, id_to_node_name, node_name_to_id

def can_skip(s,p,o):
    if o[0] == '"':
        return True
    return False